from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from apps.authentication.models import User
from ..models import (Profile, FriendRequest, Post, Group, ActivityFeed, Recommendation,
                     LanguageExchangeSession, StudySession, LanguagePartnerMatch)


class CommunityMainView(LoginRequiredMixin, TemplateView):
    """Page principale de la communauté"""
    template_name = 'community/main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtenir ou créer le profil utilisateur
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        
        # App info pour le header
        current_app_info = {
            'name': 'community',
            'display_name': 'Community',
            'static_icon': '/app-icons/community/icon.png',
            'route_path': '/community/'
        }
        
        context.update({
            'current_app': current_app_info,
            'profile': profile,
            'friend_requests_count': profile.friend_requests_received().filter(status='pending').count(),
            'friends_count': profile.friends.count(),
            'recent_posts': Post.objects.filter(
                author__in=[f.user for f in profile.friends.all()]
            )[:5],
            'suggested_friends': profile.suggest_friends()[:3],
        })
        return context


class DiscoverUsersView(LoginRequiredMixin, ListView):
    """Page de découverte d'utilisateurs"""
    model = User
    template_name = 'community/discover.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        # Obtenir ou créer le profil utilisateur
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        
        # Exclure l'utilisateur actuel et ses amis actuels
        excluded_users = [self.request.user.id] + list(profile.friends.values_list('user_id', flat=True))
        
        queryset = User.objects.exclude(id__in=excluded_users).filter(is_active=True)
        
        # Filtres de recherche
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Filtre par langue native
        native_language = self.request.GET.get('native_language')
        if native_language:
            queryset = queryset.filter(native_language=native_language)
            
        # Filtre par langue cible
        target_language = self.request.GET.get('target_language')
        if target_language:
            queryset = queryset.filter(target_language=target_language)
        
        return queryset.select_related('profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ajouter les choix de langues pour les filtres
        from apps.authentication.models import LANGUAGE_CHOICES
        context['language_choices'] = LANGUAGE_CHOICES
        
        # Paramètres de recherche actuels
        context['current_search'] = self.request.GET.get('search', '')
        context['current_native_language'] = self.request.GET.get('native_language', '')
        context['current_target_language'] = self.request.GET.get('target_language', '')
        
        return context


class FriendsListView(LoginRequiredMixin, TemplateView):
    """Liste des amis de l'utilisateur"""
    template_name = 'community/friends.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtenir ou créer le profil utilisateur
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        
        context.update({
            'profile': profile,
            'friends': profile.friends.all(),
            'pending_requests': profile.friend_requests_received().filter(status='pending'),
            'sent_requests': profile.friend_requests_sent().filter(status='pending'),
        })
        return context


class FriendRequestsView(LoginRequiredMixin, TemplateView):
    """Gestion des demandes d'amitié"""
    template_name = 'community/friend_requests.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        
        context.update({
            'received_requests': profile.friend_requests_received().filter(status='pending'),
            'sent_requests': profile.friend_requests_sent().filter(status='pending'),
        })
        return context


class MessagesView(LoginRequiredMixin, TemplateView):
    """Page des messages privés"""
    template_name = 'community/messages.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        
        context.update({
            'conversations': profile.conversations.all(),
            'unread_count': profile.unread_messages().count(),
        })
        return context


class GroupsView(LoginRequiredMixin, ListView):
    """Page des groupes"""
    model = Group
    template_name = 'community/groups.html'
    context_object_name = 'groups'
    paginate_by = 10
    
    def get_queryset(self):
        return Group.objects.all().prefetch_related('members')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        context['my_groups'] = profile.groups.all()
        
        return context


class ActivityFeedView(LoginRequiredMixin, ListView):
    """Flux d'activités des amis"""
    model = ActivityFeed
    template_name = 'community/feed.html'
    context_object_name = 'activities'
    paginate_by = 20
    
    def get_queryset(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        
        # Activités des amis
        friends_profiles = profile.friends.all()
        
        return ActivityFeed.objects.filter(
            profile__in=friends_profiles
        ).select_related('profile__user').order_by('-created_at')


class UserProfileView(LoginRequiredMixin, TemplateView):
    """View for displaying user profiles with language learning focus"""
    template_name = 'community/user_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the profile user
        username = kwargs.get('username')
        try:
            # Recherche case-insensitive pour les usernames
            profile_user = User.objects.get(username__iexact=username)
            profile, created = Profile.objects.get_or_create(user=profile_user)
        except User.DoesNotExist:
            raise Http404("User not found")
        
        # Get current user profile
        current_user_profile, _ = Profile.objects.get_or_create(user=self.request.user)
        
        # Check friendship status
        is_friend = profile in current_user_profile.friends.all()
        friend_request_pending = FriendRequest.objects.filter(
            Q(sender=self.request.user, receiver=profile_user, status='pending') |
            Q(sender=profile_user, receiver=self.request.user, status='pending')
        ).exists()
        
        # Calculate language exchange compatibility
        compatibility_score = 0
        compatibility_reasons = []
        compatibility_badge_color = 'secondary'
        
        if self.request.user != profile_user:
            # Perfect mutual exchange
            if (self.request.user.native_language == profile_user.target_language and
                self.request.user.target_language == profile_user.native_language):
                compatibility_score = 100
                compatibility_reasons.append(f"Perfect language exchange match!")
                compatibility_badge_color = 'success'
            
            # One-way teaching opportunities
            elif self.request.user.native_language == profile_user.target_language:
                compatibility_score = 70
                compatibility_reasons.append(f"You can help with {self.request.user.get_native_language_display()}")
                compatibility_badge_color = 'primary'
            
            elif profile_user.native_language == self.request.user.target_language:
                compatibility_score = 70
                compatibility_reasons.append(f"They can help with {profile_user.get_native_language_display()}")
                compatibility_badge_color = 'primary'
            
            # Same learning language
            elif self.request.user.target_language == profile_user.target_language:
                compatibility_score = 40
                compatibility_reasons.append(f"Both learning {self.request.user.get_target_language_display()}")
                compatibility_badge_color = 'info'
        
        # Get activity statistics
        exchange_sessions_count = LanguageExchangeSession.objects.filter(
            participants=profile
        ).count()
        
        study_sessions_count = StudySession.objects.filter(
            participants=profile
        ).count()
        
        # Get recent activities
        recent_activities = ActivityFeed.objects.filter(
            profile=profile
        ).order_by('-created_at')[:10]
        
        context.update({
            'profile_user': profile_user,
            'profile': profile,
            'is_friend': is_friend,
            'friend_request_pending': friend_request_pending,
            'compatibility_score': compatibility_score,
            'compatibility_reasons': compatibility_reasons,
            'compatibility_badge_color': compatibility_badge_color,
            'exchange_sessions_count': exchange_sessions_count,
            'study_sessions_count': study_sessions_count,
            'recent_activities': recent_activities,
        })
        
        return context


# API Views pour les actions AJAX
@login_required
@require_POST
def send_friend_request(request, user_id):
    """Envoyer une demande d'amitié"""
    try:
        receiver = get_object_or_404(User, id=user_id)
        
        # Vérifier si une demande n'existe pas déjà
        existing_request = FriendRequest.objects.filter(
            Q(sender=request.user, receiver=receiver) |
            Q(sender=receiver, receiver=request.user)
        ).first()
        
        if existing_request:
            return JsonResponse({'error': 'Friend request already exists'}, status=400)
        
        # Créer la demande
        friend_request = FriendRequest.objects.create(
            sender=request.user,
            receiver=receiver
        )
        
        return JsonResponse({'success': True, 'message': 'Friend request sent!'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST  
def accept_friend_request(request, request_id):
    """Accepter une demande d'amitié"""
    try:
        friend_request = get_object_or_404(
            FriendRequest, 
            id=request_id, 
            receiver=request.user,
            status='pending'
        )
        
        # Accepter la demande
        friend_request.status = 'accepted'
        friend_request.save()
        
        # Ajouter les utilisateurs comme amis mutuellement
        sender_profile, _ = Profile.objects.get_or_create(user=friend_request.sender)
        receiver_profile, _ = Profile.objects.get_or_create(user=friend_request.receiver)
        
        sender_profile.friends.add(receiver_profile)
        receiver_profile.friends.add(sender_profile)
        
        return JsonResponse({'success': True, 'message': 'Friend request accepted!'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def reject_friend_request(request, request_id):
    """Rejeter une demande d'amitié"""
    try:
        friend_request = get_object_or_404(
            FriendRequest,
            id=request_id,
            receiver=request.user,
            status='pending'
        )
        
        friend_request.status = 'rejected'
        friend_request.save()
        
        return JsonResponse({'success': True, 'message': 'Friend request rejected'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)