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
                     LanguageExchangeSession, StudySession, LanguagePartnerMatch, GroupMessage)


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
        
        # Check if user is new (no friends yet)
        is_new_user = profile.friends.count() == 0
        
        # Get smart friend suggestions
        suggested_friends = profile.suggest_friends(limit=6)
        
        # Get perfect language exchange partners for new users
        suggested_partners = []
        if is_new_user and hasattr(self.request.user, 'native_language') and hasattr(self.request.user, 'target_language'):
            # Find perfect language exchange matches
            suggested_partners = Profile.objects.filter(
                user__native_language=self.request.user.target_language,
                user__target_language=self.request.user.native_language
            ).exclude(id=profile.id)[:3]
        
        context.update({
            'current_app': current_app_info,
            'profile': profile,
            'friend_requests_count': profile.friend_requests_received().filter(status='pending').count(),
            'friends_count': profile.friends.count(),
            'recent_posts': Post.objects.all().select_related('author')[:10],
            'suggested_friends': suggested_friends,
            'is_new_user': is_new_user,
            'suggested_partners': suggested_partners,
            'has_profile_completed': bool(
                getattr(self.request.user, 'native_language', None) and 
                getattr(self.request.user, 'target_language', None)
            ),
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
        
        friends = profile.friends.all()
        online_friends_count = sum(1 for friend in friends if friend.is_online)
        
        context.update({
            'profile': profile,
            'friends': friends,
            'pending_requests': profile.friend_requests_received().filter(status='pending'),
            'sent_requests': profile.friend_requests_sent().filter(status='pending'),
            'online_friends_count': online_friends_count,
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


@login_required
@require_POST
def create_group(request):
    """Créer un nouveau groupe d'étude"""
    try:
        import json
        data = json.loads(request.body)
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        language = data.get('language', '').strip()
        difficulty_level = data.get('difficulty_level', '').strip()
        group_type = data.get('group_type', '').strip()
        
        # Validation
        if not name:
            return JsonResponse({'error': 'Group name is required'}, status=400)
        if not description:
            return JsonResponse({'error': 'Description is required'}, status=400)
        if not language:
            return JsonResponse({'error': 'Language is required'}, status=400)
            
        # Obtenir ou créer le profil utilisateur
        creator_profile, _ = Profile.objects.get_or_create(user=request.user)
        
        # Vérifier si un groupe avec ce nom existe déjà
        if Group.objects.filter(name=name).exists():
            return JsonResponse({'error': f'A group named "{name}" already exists. Please choose a different name.'}, status=400)

        # Créer le groupe
        group = Group.objects.create(
            name=name,
            description=description,
            language=language.upper(),  # Le modèle utilise des codes en majuscules
            level=difficulty_level or 'mixed',
            group_type=group_type or 'general',
            created_by=creator_profile
        )
        
        # Ajouter le créateur comme membre du groupe
        creator_profile.groups.add(group)
        
        return JsonResponse({
            'success': True, 
            'message': 'Group created successfully!',
            'group': {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'language': group.get_language_display() if hasattr(group, 'get_language_display') else group.language,
                'members_count': group.members.count()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class GroupDetailView(LoginRequiredMixin, TemplateView):
    """Vue détaillée d'un groupe avec chat intelligent"""
    template_name = 'community/group_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_id = kwargs.get('group_id')
        
        try:
            group = get_object_or_404(Group, id=group_id)
            profile, _ = Profile.objects.get_or_create(user=self.request.user)
            
            # Vérifier si l'utilisateur est membre du groupe
            is_member = profile in group.members.all()
            is_creator = group.created_by == profile
            is_moderator = profile in group.moderators.all() if hasattr(group, 'moderators') else False
            
            if not is_member and not group.is_private:
                # Auto-join pour les groupes publics
                profile.groups.add(group)
                is_member = True
                
            # Récupérer les vrais messages du groupe
            recent_messages = group.messages.select_related('sender__user').order_by('-timestamp')[:50]
            
            context.update({
                'group': group,
                'is_member': is_member,
                'is_creator': is_creator,
                'is_moderator': is_moderator,
                'members_count': group.members.count(),
                'online_members': group.members.filter(is_online=True),
                'recent_messages': recent_messages,
            })
            
        except Group.DoesNotExist:
            raise Http404("Group not found")
            
        return context


@login_required
@require_POST
def send_group_message(request, group_id):
    """Envoyer un message dans un groupe"""
    try:
        import json
        data = json.loads(request.body)
        
        message_text = data.get('message', '').strip()
        if not message_text:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
        # Vérifier que le groupe existe
        group = get_object_or_404(Group, id=group_id)
        
        # Vérifier que l'utilisateur est membre du groupe
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile not in group.members.all():
            return JsonResponse({'error': 'You are not a member of this group'}, status=403)
            
        # Créer le message
        group_message = GroupMessage.objects.create(
            group=group,
            sender=profile,
            message=message_text
        )
        
        # Retourner le message créé
        return JsonResponse({
            'success': True,
            'message': {
                'id': group_message.id,
                'sender_name': group_message.sender.user.get_full_name() or group_message.sender.user.username,
                'sender_avatar': group_message.sender.user.username[0].upper(),
                'sender_avatar_url': group_message.sender.avatar.url if group_message.sender.avatar else None,
                'message': group_message.message,
                'timestamp': group_message.timestamp.isoformat(),
                'time_display': 'now'
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_group_messages(request, group_id):
    """Récupérer les messages d'un groupe"""
    try:
        group = get_object_or_404(Group, id=group_id)
        
        # Vérifier que l'utilisateur est membre du groupe
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile not in group.members.all():
            return JsonResponse({'error': 'You are not a member of this group'}, status=403)
            
        # Récupérer les messages
        messages = group.messages.select_related('sender__user').order_by('timestamp')
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'sender_name': msg.sender.user.get_full_name() or msg.sender.user.username,
                'sender_avatar': msg.sender.user.username[0].upper(),
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat(),
                'is_own': msg.sender == profile
            })
            
        return JsonResponse({
            'success': True,
            'messages': messages_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def promote_to_moderator(request, group_id, user_id):
    """Promouvoir un membre comme modérateur (seuls les créateurs peuvent faire cela)"""
    try:
        group = get_object_or_404(Group, id=group_id)
        target_profile = get_object_or_404(Profile, id=user_id)
        current_profile, _ = Profile.objects.get_or_create(user=request.user)
        
        # Vérifier que l'utilisateur actuel est le créateur du groupe
        if group.created_by != current_profile:
            return JsonResponse({'error': 'Only group creators can promote moderators'}, status=403)
        
        # Vérifier que l'utilisateur cible est membre du groupe
        if target_profile not in group.members.all():
            return JsonResponse({'error': 'User must be a group member'}, status=400)
        
        # Ajouter comme modérateur
        group.moderators.add(target_profile)
        
        return JsonResponse({
            'success': True,
            'message': f'{target_profile.user.get_full_name() or target_profile.user.username} is now a moderator'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def remove_moderator(request, group_id, user_id):
    """Retirer les droits de modérateur (seuls les créateurs peuvent faire cela)"""
    try:
        group = get_object_or_404(Group, id=group_id)
        target_profile = get_object_or_404(Profile, id=user_id)
        current_profile, _ = Profile.objects.get_or_create(user=request.user)
        
        # Vérifier que l'utilisateur actuel est le créateur du groupe
        if group.created_by != current_profile:
            return JsonResponse({'error': 'Only group creators can remove moderators'}, status=403)
        
        # Retirer des modérateurs
        group.moderators.remove(target_profile)
        
        return JsonResponse({
            'success': True,
            'message': f'{target_profile.user.get_full_name() or target_profile.user.username} is no longer a moderator'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST 
def remove_group_member(request, group_id, user_id):
    """Retirer un membre du groupe (créateurs et modérateurs peuvent faire cela)"""
    try:
        group = get_object_or_404(Group, id=group_id)
        target_profile = get_object_or_404(Profile, id=user_id)
        current_profile, _ = Profile.objects.get_or_create(user=request.user)
        
        # Vérifier les permissions
        is_creator = group.created_by == current_profile
        is_moderator = current_profile in group.moderators.all()
        
        if not (is_creator or is_moderator):
            return JsonResponse({'error': 'Only creators and moderators can remove members'}, status=403)
            
        # Ne pas permettre de retirer le créateur
        if target_profile == group.created_by:
            return JsonResponse({'error': 'Cannot remove group creator'}, status=400)
        
        # Retirer du groupe et des modérateurs si applicable
        group.members.remove(target_profile)
        group.moderators.remove(target_profile)  # Au cas où il était modérateur
        
        return JsonResponse({
            'success': True,
            'message': f'{target_profile.user.get_full_name() or target_profile.user.username} has been removed from the group'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def update_group_settings(request, group_id):
    """Mettre à jour les paramètres du groupe"""
    try:
        group = get_object_or_404(Group, id=group_id)
        current_profile, _ = Profile.objects.get_or_create(user=request.user)
        
        # Vérifier les permissions
        is_creator = group.created_by == current_profile
        is_moderator = current_profile in group.moderators.all()
        
        if not (is_creator or is_moderator):
            return JsonResponse({'error': 'Only creators and moderators can update group settings'}, status=403)
        
        # Si c'est un upload d'avatar (multipart/form-data)
        if 'avatar' in request.FILES:
            group.avatar = request.FILES['avatar']
            group.save()
            return JsonResponse({
                'success': True,
                'message': 'Group avatar updated successfully!',
                'avatar_url': group.avatar.url if group.avatar else None
            })
        
        # Sinon, c'est une mise à jour JSON des autres paramètres
        import json
        data = json.loads(request.body)
        
        # Mettre à jour les champs
        if 'name' in data:
            group.name = data['name'].strip()
        if 'description' in data:
            group.description = data['description'].strip()
        if 'language' in data:
            group.language = data['language']
        if 'level' in data:
            group.level = data['level']
            
        group.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Group settings updated successfully!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def delete_group(request, group_id):
    """Supprimer un groupe (seuls les créateurs peuvent faire cela)"""
    try:
        group = get_object_or_404(Group, id=group_id)
        current_profile, _ = Profile.objects.get_or_create(user=request.user)
        
        # Vérifier que l'utilisateur actuel est le créateur du groupe
        if group.created_by != current_profile:
            return JsonResponse({'error': 'Only group creators can delete groups'}, status=403)
        
        # Supprimer le groupe
        group_name = group.name
        group.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Group "{group_name}" has been deleted successfully!',
            'redirect_url': '/community/groups/'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class GroupManageView(LoginRequiredMixin, TemplateView):
    """Vue de gestion d'un groupe (pour les créateurs/modérateurs)"""
    template_name = 'community/group_manage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_id = kwargs.get('group_id')
        
        try:
            group = get_object_or_404(Group, id=group_id)
            profile, _ = Profile.objects.get_or_create(user=self.request.user)
            
            # Vérifier les permissions
            is_creator = group.created_by == profile
            is_moderator = profile in group.moderators.all()
            
            if not (is_creator or is_moderator):
                raise Http404("You don't have permission to manage this group")
                
            context.update({
                'group': group,
                'is_creator': is_creator,
                'is_moderator': is_moderator,
                'members': group.members.all(),
                'pending_requests': [],  # TODO: Implémenter les demandes d'adhésion
                'group_stats': {
                    'total_messages': group.messages.count() if hasattr(group, 'messages') else 0,
                    'active_members': group.members.filter(is_online=True).count(),
                    'total_members': group.members.count(),
                }
            })
            
        except Group.DoesNotExist:
            raise Http404("Group not found")
            
        return context