from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from ..models import Document, Folder, DocumentShare
from ..serializers import DocumentSerializer
from ..forms import DocumentForm, FolderForm
import logging

logger = logging.getLogger(__name__)


def get_folders_context(user):
    """Helper function to get folders for sidebar"""
    return Folder.objects.filter(
        owner=user
    ).order_by('name')[:10]  # Limit to 10 recent folders for performance


class DocumentsContextMixin:
    """Mixin to add common context data for all documents views"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Always add folders for sidebar
        context['folders'] = get_folders_context(self.request.user)
        
        return context


class DocumentListView(DocumentsContextMixin, LoginRequiredMixin, ListView):
    """Web view for listing documents"""
    
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        """Return documents accessible by the current user"""
        user = self.request.user
        
        queryset = Document.objects.filter(
            Q(owner=user) | 
            Q(shares__user=user)
        ).distinct().select_related(
            'owner', 'last_edited_by', 'folder'
        ).order_by('-updated_at')
        
        # Apply filters
        folder_id = self.request.GET.get('folder')
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
            
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(tags__icontains=search)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add current folder if filtering by folder
        folder_id = self.request.GET.get('folder')
        if folder_id:
            try:
                context['current_folder'] = Folder.objects.get(
                    id=folder_id, 
                    owner=self.request.user
                )
            except Folder.DoesNotExist:
                pass
                
        # Add search query for template
        context['search_query'] = self.request.GET.get('search', '')
        
        return context


class DocumentDetailView(DocumentsContextMixin, LoginRequiredMixin, DetailView):
    """Web view for document details"""
    
    model = Document
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'
    
    def get_queryset(self):
        """Ensure user can access this document"""
        user = self.request.user
        return Document.objects.filter(
            Q(owner=user) | 
            Q(shares__user=user)
        ).select_related(
            'owner', 'last_edited_by', 'folder'
        ).prefetch_related(
            'shares__user', 'comments__author'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check user permissions
        document = self.object
        user = self.request.user
        
        context['can_edit'] = (
            document.owner == user or
            document.shares.filter(
                user=user,
                permission_level__in=['edit', 'admin']
            ).exists()
        )
        
        context['can_share'] = (
            document.owner == user or
            document.shares.filter(
                user=user,
                permission_level='admin'
            ).exists()
        )
        
        context['can_delete'] = document.owner == user
        
        # Add collaborators info
        context['collaborators'] = document.shares.select_related(
            'user', 'shared_by'
        ).all()
        
        # Add comments (top-level only, replies handled in template)
        context['comments'] = document.comments.filter(
            parent__isnull=True
        ).select_related(
            'author', 'resolved_by'
        ).prefetch_related('replies__author')
        
        return context


class DocumentCreateView(DocumentsContextMixin, LoginRequiredMixin, CreateView):
    """Web view for creating documents"""
    
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.last_edited_by = self.request.user
        messages.success(self.request, 'Document créé avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('documents:document_detail', kwargs={'pk': self.object.pk})


class DocumentEditView(DocumentsContextMixin, LoginRequiredMixin, UpdateView):
    """Web view for editing documents"""
    
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    
    def get_queryset(self):
        """Ensure user can edit this document"""
        user = self.request.user
        return Document.objects.filter(
            Q(owner=user) | 
            Q(shares__user=user, shares__permission_level__in=['edit', 'admin'])
        )
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.last_edited_by = self.request.user
        messages.success(self.request, 'Document modifié avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('documents:document_detail', kwargs={'pk': self.object.pk})


class DocumentDeleteView(DocumentsContextMixin, LoginRequiredMixin, DeleteView):
    """Web view for deleting documents"""
    
    model = Document
    template_name = 'documents/document_confirm_delete.html'
    success_url = reverse_lazy('documents:document_list')
    
    def get_queryset(self):
        """Only owners can delete documents"""
        return Document.objects.filter(owner=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Document supprimé avec succès!')
        return super().delete(request, *args, **kwargs)


@login_required
def document_editor(request, pk):
    """Advanced document editor view with live preview"""
    
    document = get_object_or_404(
        Document.objects.filter(
            Q(owner=request.user) | 
            Q(shares__user=request.user, shares__permission_level__in=['edit', 'admin'])
        ).select_related('owner', 'last_edited_by', 'folder'),
        pk=pk
    )
    
    # Check edit permissions
    can_edit = (
        document.owner == request.user or
        document.shares.filter(
            user=request.user,
            permission_level__in=['edit', 'admin']
        ).exists()
    )
    
    if not can_edit:
        return HttpResponseForbidden("Vous n'avez pas les droits pour modifier ce document")
    
    context = {
        'document': document,
        'can_edit': can_edit,
        'folders': get_folders_context(request.user),
    }
    
    return render(request, 'documents/document_edit.html', context)


@login_required
def folder_list(request):
    """View for managing folders"""
    
    all_folders = Folder.objects.filter(
        owner=request.user
    ).select_related('parent').order_by('name')
    
    context = {
        'folders': get_folders_context(request.user),  # For sidebar
        'all_folders': all_folders,  # For main content
    }
    
    return render(request, 'documents/folder_list.html', context)


@login_required
def document_share(request, pk):
    """View for managing document sharing"""
    
    document = get_object_or_404(
        Document.objects.filter(
            Q(owner=request.user) |
            Q(shares__user=request.user, shares__permission_level='admin')
        ),
        pk=pk
    )
    
    shares = document.shares.select_related(
        'user', 'shared_by'
    ).all()
    
    context = {
        'document': document,
        'shares': shares,
        'folders': get_folders_context(request.user),
    }
    
    return render(request, 'documents/document_share.html', context)


@login_required
def main_view(request):
    """Main documents dashboard"""
    
    # Recent documents
    recent_documents = Document.objects.filter(
        Q(owner=request.user) | 
        Q(shares__user=request.user)
    ).distinct().select_related(
        'owner', 'last_edited_by', 'folder'
    ).order_by('-updated_at')[:5]
    
    # User's folders for main content
    user_folders = Folder.objects.filter(
        owner=request.user
    ).order_by('name')[:10]
    
    # Shared with user recently
    shared_documents = Document.objects.filter(
        shares__user=request.user
    ).select_related(
        'owner', 'folder'
    ).order_by('-shares__shared_at')[:5]
    
    context = {
        'recent_documents': recent_documents,
        'folders': get_folders_context(request.user),  # For sidebar
        'user_folders': user_folders,  # For main content
        'shared_documents': shared_documents,
    }
    
    return render(request, 'documents/main.html', context)