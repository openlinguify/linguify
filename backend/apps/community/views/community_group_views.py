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
from ..models import (Profile, Group, GroupMessage)


class GroupsView(LoginRequiredMixin, ListView):
    """Page des groupes"""
    model = Group
    template_name = 'community/group/groups.html'
    context_object_name = 'groups'
    paginate_by = 10
    
    def get_queryset(self):
        return Group.objects.all().prefetch_related('members')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        context['my_groups'] = profile.groups.all()
        
        return context


class GroupDetailView(LoginRequiredMixin, TemplateView):
    """Vue détaillée d'un groupe avec chat intelligent"""
    template_name = 'community/group/group_detail.html'
    
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


class GroupManageView(LoginRequiredMixin, TemplateView):
    """Vue de gestion d'un groupe (pour les créateurs/modérateurs)"""
    template_name = 'community/group/group_manage.html'
    
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


# API Views pour les actions AJAX des groupes

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
        
        # Retourner le message créé avec avatar de l'utilisateur (même méthode que le header)
        # Utiliser get_profile_picture_url qui priorise Supabase puis le stockage local
        avatar_url = group_message.sender.user.get_profile_picture_url
        if not avatar_url and group_message.sender.avatar:
            avatar_url = group_message.sender.avatar.url
        
            
        return JsonResponse({
            'success': True,
            'message': {
                'id': group_message.id,
                'sender_name': group_message.sender.user.get_full_name() or group_message.sender.user.username,
                'sender_avatar': group_message.sender.user.username[0].upper(),
                'sender_avatar_url': avatar_url,
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