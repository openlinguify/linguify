from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import LanguagelearningItem
from .forms import LanguagelearningItemForm


@login_required
def language_learning_home(request):
    """Page d'accueil de Language Learning"""
    items = LanguagelearningItem.objects.filter(
        user=request.user,
        is_active=True
    )
    
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_items = paginator.get_page(page_number)
    
    context = {
        'items': page_items,
        'total_items': items.count(),
        'app_name': 'Language Learning',
    }
    return render(request, 'language_learning/home.html', context)


@login_required
def create_item(request):
    """Créer un nouvel item"""
    if request.method == 'POST':
        form = LanguagelearningItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f'{item.title} créé avec succès!')
            return redirect('language_learning_home')
    else:
        form = LanguagelearningItemForm()
    
    return render(request, 'language_learning/create_item.html', {'form': form})


@login_required
def edit_item(request, item_id):
    """Modifier un item"""
    item = get_object_or_404(LanguagelearningItem, id=item_id, user=request.user)
    
    if request.method == 'POST':
        form = LanguagelearningItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'{item.title} modifié avec succès!')
            return redirect('language_learning_home')
    else:
        form = LanguagelearningItemForm(instance=item)
    
    return render(request, 'language_learning/edit_item.html', {'form': form, 'item': item})


@login_required
def delete_item(request, item_id):
    """Supprimer un item"""
    item = get_object_or_404(LanguagelearningItem, id=item_id, user=request.user)
    
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f'{title} supprimé avec succès!')
        return redirect('language_learning_home')
    
    return render(request, 'language_learning/confirm_delete.html', {'item': item})


# API Views
@login_required
def api_items(request):
    """API pour récupérer les items"""
    items = LanguagelearningItem.objects.filter(
        user=request.user,
        is_active=True
    ).values('id', 'title', 'description', 'created_at')
    
    return JsonResponse({
        'items': list(items),
        'count': len(items)
    })
