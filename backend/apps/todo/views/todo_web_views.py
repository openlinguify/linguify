from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count
from ..models.todo_models import Task, Project, PersonalStageType, Tag, Category


class TodoMainView(LoginRequiredMixin, TemplateView):
    """Main Todo interface - intelligent view router"""
    
    def get(self, request, *args, **kwargs):
        # Redirect main todo URL to kanban view by default
        from django.shortcuts import redirect
        return redirect('todo_web:kanban')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's default view preference from settings
        default_view = self.request.GET.get('view', 'kanban')  # Default to kanban
        
        # Ensure user has personal stages
        if not PersonalStageType.objects.filter(user=user).exists():
            PersonalStageType.create_default_stages(user)
        
        # Basic statistics for dashboard
        tasks = Task.objects.filter(user=user, active=True)
        today = timezone.now().date()
        
        context.update({
            'current_view': default_view,
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(state='1_done').count(),
            'due_today': tasks.filter(due_date__date=today).count(),
            'overdue': tasks.filter(
                due_date__lt=timezone.now(),
                state__in=['1_todo', '1_in_progress']
            ).count(),
            'personal_stages': PersonalStageType.objects.filter(user=user).order_by('sequence'),
            'projects': Project.objects.filter(user=user, status='active'),
            'categories': Category.objects.filter(user=user),
            'popular_tags': Tag.objects.filter(user=user).annotate(
                usage_count=Count('tasks')
            ).order_by('-usage_count')[:10],
        })
        
        return context


class TodoKanbanView(LoginRequiredMixin, TemplateView):
    """Kanban board view - Odoo-style"""
    template_name = 'todo/views/kanban.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Ensure personal stages exist
        stages = PersonalStageType.objects.filter(user=user).order_by('sequence')
        if not stages.exists():
            PersonalStageType.create_default_stages(user)
            stages = PersonalStageType.objects.filter(user=user).order_by('sequence')
        
        # Get tasks grouped by stages
        kanban_data = {}
        for stage in stages:
            stage_tasks = Task.objects.filter(
                user=user,
                personal_stage_type=stage,
                active=True
            ).order_by('sequence', '-created_at')
            
            kanban_data[stage.id] = {
                'stage': stage,
                'tasks': stage_tasks,
                'count': stage_tasks.count()
            }
        
        context.update({
            'kanban_data': kanban_data,
            'stages': stages,
            'view_mode': 'kanban',
            'can_create': True,
            'can_edit': True,
        })
        
        return context


class TodoListView(LoginRequiredMixin, TemplateView):
    """List view - Odoo-style editable list"""
    template_name = 'todo/views/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get tasks with filters
        tasks = Task.objects.filter(user=user, active=True)
        
        # Apply filters from query params
        project_filter = self.request.GET.get('project')
        if project_filter:
            tasks = tasks.filter(project_id=project_filter)
        
        stage_filter = self.request.GET.get('stage')
        if stage_filter:
            tasks = tasks.filter(personal_stage_type_id=stage_filter)
        
        priority_filter = self.request.GET.get('priority')
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        
        status_filter = self.request.GET.get('status')
        if status_filter == 'open':
            tasks = tasks.exclude(state__in=['1_done', '1_canceled'])
        elif status_filter == 'closed':
            tasks = tasks.filter(state__in=['1_done', '1_canceled'])
        
        # Search
        search = self.request.GET.get('search')
        if search:
            tasks = tasks.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Order by with direction support
        order_by = self.request.GET.get('order_by', 'state')
        order_dir = self.request.GET.get('order_dir', 'asc')
        
        # Determine direction prefix
        dir_prefix = '' if order_dir == 'asc' else '-'
        
        # Apply sorting based on field and direction
        if order_by == 'due_date':
            if order_dir == 'asc':
                tasks = tasks.order_by('due_date', 'created_at')
            else:
                tasks = tasks.order_by('-due_date', '-created_at')
        elif order_by == 'priority':
            if order_dir == 'asc':
                tasks = tasks.order_by('priority', 'due_date')  # 0 first, then 1
            else:
                tasks = tasks.order_by('-priority', 'due_date')  # 1 first, then 0
        elif order_by == 'title':
            tasks = tasks.order_by(f'{dir_prefix}title')
        elif order_by == 'state':
            tasks = tasks.order_by(f'{dir_prefix}state', '-priority', 'due_date')
        elif order_by == 'personal_stage_type__name':
            tasks = tasks.order_by(f'{dir_prefix}personal_stage_type__name', 'title')
        elif order_by == 'project__name':
            # Handle null projects properly - nulls always go to end
            from django.db.models import F
            if order_dir == 'asc':
                tasks = tasks.order_by(F('project__name').asc(nulls_last=True), 'title')
            else:
                tasks = tasks.order_by(F('project__name').desc(nulls_last=True), 'title')
        elif order_by == 'created':
            tasks = tasks.order_by(f'{dir_prefix}created_at')
        else:  # default: state
            tasks = tasks.order_by('state', '-priority', 'due_date')
        
        context.update({
            'tasks': tasks,
            'view_mode': 'list',
            'projects': Project.objects.filter(user=user, status='active'),
            'stages': PersonalStageType.objects.filter(user=user).order_by('sequence'),
            'current_filters': {
                'project': project_filter,
                'stage': stage_filter,
                'priority': priority_filter,
                'status': status_filter,
                'search': search,
                'order_by': order_by,
                'order_dir': order_dir,
            },
            'can_create': True,
            'can_edit': True,
        })
        
        return context


class TodoActivityView(LoginRequiredMixin, TemplateView):
    """Activity/Timeline view - Odoo-style activity tracking"""
    template_name = 'todo/views/activity.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Recently created tasks
        recent_tasks = Task.objects.filter(
            user=user,
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:20]
        
        # Recently completed tasks
        completed_tasks = Task.objects.filter(
            user=user,
            state='1_done',
            completed_at__gte=thirty_days_ago
        ).order_by('-completed_at')[:20]
        
        # Overdue tasks
        overdue_tasks = Task.objects.filter(
            user=user,
            due_date__lt=timezone.now(),
            state__in=['1_todo', '1_in_progress'],
            active=True
        ).order_by('due_date')
        
        # Due today
        today = timezone.now().date()
        due_today_tasks = Task.objects.filter(
            user=user,
            due_date__date=today,
            state__in=['1_todo', '1_in_progress'],
            active=True
        ).order_by('due_date')
        
        # Due this week
        week_end = today + timedelta(days=7)
        due_week_tasks = Task.objects.filter(
            user=user,
            due_date__date__range=[today, week_end],
            state__in=['1_todo', '1_in_progress'],
            active=True
        ).exclude(due_date__date=today).order_by('due_date')
        
        # Activity statistics
        stats = {
            'tasks_created_today': Task.objects.filter(
                user=user,
                created_at__date=today
            ).count(),
            'tasks_completed_today': Task.objects.filter(
                user=user,
                completed_at__date=today
            ).count(),
            'tasks_created_this_week': Task.objects.filter(
                user=user,
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'tasks_completed_this_week': Task.objects.filter(
                user=user,
                completed_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }
        
        context.update({
            'recent_tasks': recent_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'due_today_tasks': due_today_tasks,
            'due_week_tasks': due_week_tasks,
            'activity_stats': stats,
            'view_mode': 'activity',
        })
        
        return context


class TodoFormView(LoginRequiredMixin, TemplateView):
    """Task creation/editing form - Odoo-style"""
    template_name = 'todo/views/form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        task_id = kwargs.get('task_id')
        
        task = None
        if task_id:
            task = get_object_or_404(Task, id=task_id, user=user)
        
        # Ensure personal stages exist
        stages = PersonalStageType.objects.filter(user=user).order_by('sequence')
        if not stages.exists():
            PersonalStageType.create_default_stages(user)
            stages = PersonalStageType.objects.filter(user=user).order_by('sequence')
        
        context.update({
            'task': task,
            'is_edit': bool(task),
            'view_mode': 'form',
            'projects': Project.objects.filter(user=user, status='active'),
            'stages': stages,
            'categories': Category.objects.filter(user=user),
            'tags': Tag.objects.filter(user=user).order_by('name'),
            'priority_choices': Task.PRIORITY_CHOICES,
            'state_choices': Task.STATE_CHOICES,
        })
        
        return context