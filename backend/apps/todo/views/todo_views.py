from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg, Max
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ..models.todo_models import Task, Project, PersonalStageType, Tag, Category, Project, Task, Note, Category, Tag, Reminder, TaskTemplate, PersonalStageType
from ..serializers import (
    ProjectListSerializer, ProjectDetailSerializer,
    TaskListSerializer, TaskDetailSerializer, TaskKanbanSerializer,
    TaskQuickCreateSerializer, TaskToggleSerializer, DashboardStatsSerializer,
    NoteSerializer, CategorySerializer, TagSerializer,
    ReminderSerializer, TaskTemplateSerializer, PersonalStageTypeSerializer
)
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404


# HTMX Helper Mixin
class HTMXResponseMixin:
    """Mixin for handling HTMX requests and responses"""
    
    def get_htmx_template(self, template_name=None):
        """Get template for HTMX partial response"""
        if template_name:
            return template_name
        return getattr(self, 'htmx_template_name', self.template_name)
    
    def render_htmx_response(self, context, template_name=None):
        """Render partial template for HTMX"""
        template = self.get_htmx_template(template_name)
        html = render_to_string(template, context, request=self.request)
        return HttpResponse(html)
    
    def is_htmx(self):
        """Check if request is from HTMX"""
        return self.request.headers.get('HX-Request') == 'true'


class TodoMainView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX-powered main Todo interface"""
    template_name = 'todo/main.html'
    
    def get(self, request, *args, **kwargs):
        # If HTMX request, return partial content
        if self.is_htmx():
            view_type = request.GET.get('view', 'kanban')
            return self.get_partial_view(request, view_type)
        
        # Full page load - show main interface
        return super().get(request, *args, **kwargs)
    
    def get_partial_view(self, request, view_type):
        """Return HTMX partial based on view type"""
        user = request.user
        
        if view_type == 'kanban':
            return self.get_kanban_partial(user)
        elif view_type == 'list':
            return self.get_list_partial(user)
        elif view_type == 'activity':
            return self.get_activity_partial(user)
        else:
            return self.get_kanban_partial(user)  # Default
    
    def get_kanban_partial(self, user):
        """Return Kanban view partial"""
        stages = PersonalStageType.objects.filter(user=user).order_by('sequence')
        if not stages.exists():
            PersonalStageType.create_default_stages(user)
            stages = PersonalStageType.objects.filter(user=user).order_by('sequence')
        
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
        
        context = {'kanban_data': kanban_data, 'stages': stages}
        return self.render_htmx_response(context, 'todo/partials/kanban_board.html')
    
    def get_list_partial(self, user):
        """Return List view partial"""
        tasks = Task.objects.filter(user=user, active=True).order_by('-created_at')
        context = {'tasks': tasks}
        return self.render_htmx_response(context, 'todo/partials/task_list.html')
    
    def get_activity_partial(self, user):
        """Return Activity view partial"""
        recent_tasks = Task.objects.filter(user=user, active=True).order_by('-updated_at')[:20]
        context = {'recent_tasks': recent_tasks}
        return self.render_htmx_response(context, 'todo/partials/activity_feed.html')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Ensure user has personal stages
        if not PersonalStageType.objects.filter(user=user).exists():
            PersonalStageType.create_default_stages(user)
        
        # Basic statistics for dashboard
        tasks = Task.objects.filter(user=user, active=True)
        today = timezone.now().date()
        
        context.update({
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
        })
        
        return context


class TodoKanbanView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX-powered Kanban board view"""
    template_name = 'todo/views/kanban.html'
    htmx_template_name = 'todo/partials/kanban_board.html'
    
    def get(self, request, *args, **kwargs):
        # If HTMX request, return partial content
        if self.is_htmx():
            return self.render_htmx_response(self.get_context_data())
        return super().get(request, *args, **kwargs)
    
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
            ).select_related('project', 'category').prefetch_related('tags').order_by('sequence', '-created_at')
            
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
            'today': timezone.now().date(),
            'projects': Project.objects.filter(user=user),
            'categories': Category.objects.filter(user=user),
        })
        
        return context


class TodoListView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX-powered List view - openlinguify-style editable list"""
    template_name = 'todo/views/list.html'
    htmx_template_name = 'todo/partials/task_list_table.html'
    
    def get(self, request, *args, **kwargs):
        # If HTMX request, return partial content
        if self.is_htmx():
            return self.render_htmx_response(self.get_context_data())
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get tasks with filters
        tasks = Task.objects.filter(user=user, active=True).select_related('project', 'personal_stage_type', 'category').prefetch_related('tags')
        
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
            'categories': Category.objects.filter(user=user),
            'today': timezone.now().date(),
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


class TodoActivityView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX-powered Activity/Timeline view - openlinguify-style activity tracking"""
    template_name = 'todo/views/activity.html'
    htmx_template_name = 'todo/partials/activity_feed.html'
    
    def get(self, request, *args, **kwargs):
        # If HTMX request, return partial content
        if self.is_htmx():
            return self.render_htmx_response(self.get_context_data())
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Recently created tasks
        recent_tasks = Task.objects.filter(
            user=user,
            created_at__gte=thirty_days_ago
        ).select_related('project', 'personal_stage_type', 'category').prefetch_related('tags').order_by('-created_at')[:20]
        
        # Recently completed tasks
        completed_tasks = Task.objects.filter(
            user=user,
            state='1_done',
            completed_at__gte=thirty_days_ago
        ).select_related('project', 'personal_stage_type', 'category').prefetch_related('tags').order_by('-completed_at')[:20]
        
        # Overdue tasks
        overdue_tasks = Task.objects.filter(
            user=user,
            due_date__lt=timezone.now(),
            state__in=['1_todo', '1_in_progress'],
            active=True
        ).select_related('project', 'personal_stage_type', 'category').prefetch_related('tags').order_by('due_date')
        
        # Due today
        today = timezone.now().date()
        due_today_tasks = Task.objects.filter(
            user=user,
            due_date__date=today,
            state__in=['1_todo', '1_in_progress'],
            active=True
        ).select_related('project', 'personal_stage_type', 'category').prefetch_related('tags').order_by('due_date')
        
        # Due this week
        week_end = today + timedelta(days=7)
        due_week_tasks = Task.objects.filter(
            user=user,
            due_date__date__range=[today, week_end],
            state__in=['1_todo', '1_in_progress'],
            active=True
        ).exclude(due_date__date=today).select_related('project', 'personal_stage_type', 'category').prefetch_related('tags').order_by('due_date')
        
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
            'today': today,
        })
        
        return context


class TodoFormView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX-powered Task creation/editing form - openlinguify-style"""
    template_name = 'todo/views/form.html'
    htmx_template_name = 'todo/partials/task_form.html'
    
    def get(self, request, *args, **kwargs):
        # If HTMX request, return partial content
        if self.is_htmx():
            return self.render_htmx_response(self.get_context_data(**kwargs))
        return super().get(request, *args, **kwargs)
    
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
            'priority_choices': Task.PRIORITY_CHOICES if hasattr(Task, 'PRIORITY_CHOICES') else [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
            'state_choices': Task.STATE_CHOICES if hasattr(Task, 'STATE_CHOICES') else [('1_todo', 'To Do'), ('1_in_progress', 'In Progress'), ('1_done', 'Done')],
        })
        
        return context














class PersonalStageTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for personal stage types - Open Linguify inspired"""
    serializer_class = PersonalStageTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PersonalStageType.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to prevent deletion of critical stages"""
        stage = self.get_object()
        user_stages = self.get_queryset()
        user_stages_count = user_stages.count()
        
        # Prevent deletion of the last stage
        if user_stages_count <= 1:
            return Response({
                'error': 'Impossible de supprimer le dernier stage. Vous devez avoir au moins un stage.',
                'type': 'LAST_STAGE_ERROR'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prevent deletion of critical system stages
        critical_stage_names = ['To Do', 'Done', 'Archive']
        if stage.name in critical_stage_names:
            return Response({
                'error': f'Impossible de supprimer le stage "{stage.name}" car il est nécessaire au bon fonctionnement de l\'application.',
                'type': 'CRITICAL_STAGE_ERROR',
                'stage_name': stage.name,
                'reason': f'Le stage "{stage.name}" est utilisé automatiquement par le système.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prevent deletion of the only closed stage (Done stage)
        if stage.is_closed:
            other_closed_stages = user_stages.filter(is_closed=True).exclude(id=stage.id)
            if not other_closed_stages.exists():
                return Response({
                    'error': 'Impossible de supprimer le dernier stage fermé. Au moins un stage fermé est nécessaire pour les tâches complétées.',
                    'type': 'LAST_CLOSED_STAGE_ERROR'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prevent deletion of the only open stage
        if not stage.is_closed:
            other_open_stages = user_stages.filter(is_closed=False).exclude(id=stage.id)
            if not other_open_stages.exists():
                return Response({
                    'error': 'Impossible de supprimer le dernier stage ouvert. Au moins un stage ouvert est nécessaire pour les nouvelles tâches.',
                    'type': 'LAST_OPEN_STAGE_ERROR'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder stages by sequence"""
        stage_ids = request.data.get('stage_ids', [])
        
        for index, stage_id in enumerate(stage_ids):
            try:
                stage = self.get_queryset().get(id=stage_id)
                stage.sequence = (index + 1) * 10
                stage.save()
            except PersonalStageType.DoesNotExist:
                continue
        
        return Response({'message': 'Stages reordered successfully'})
    
    @action(detail=True, methods=['post'])
    def reorder_tasks(self, request, pk=None):
        """Reorder tasks within a stage"""
        stage = self.get_object()
        task_ids = request.data.get('task_ids', [])
        
        # Import Task model here to avoid circular imports
        from ..models import Task
        
        for index, task_id in enumerate(task_ids):
            try:
                task = Task.objects.get(
                    id=task_id, 
                    user=request.user, 
                    personal_stage_type=stage
                )
                task.sequence = (index + 1) * 10
                task.save()
            except Task.DoesNotExist:
                continue
        
        return Response({'message': 'Tasks reordered successfully'})
    
    @action(detail=True, methods=['post'])
    def toggle_fold(self, request, pk=None):
        """Toggle stage fold state - Odoo kanban style"""
        stage = self.get_object()
        fold_state = request.data.get('fold', not stage.fold)
        
        stage.fold = fold_state
        stage.save(update_fields=['fold'])
        
        return Response({
            'success': True,
            'stage_id': str(stage.id),
            'fold': stage.fold,
            'message': f'Stage {"plié" if stage.fold else "déplié"} avec succès'
        })


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most used tags"""
        popular_tags = self.get_queryset().annotate(
            usage_count=Count('tasks') + Count('notes')
        ).order_by('-usage_count')[:10]
        
        serializer = self.get_serializer(popular_tags, many=True)
        return Response(serializer.data)


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Project.objects.filter(user=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter favorites
        favorites_only = self.request.query_params.get('favorites')
        if favorites_only == 'true':
            queryset = queryset.filter(is_favorite=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle project favorite status"""
        project = self.get_object()
        project.is_favorite = not project.is_favorite
        project.save()
        
        serializer = self.get_serializer(project)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark project as completed"""
        project = self.get_object()
        project.status = 'completed'
        project.completed_at = timezone.now()
        project.save()
        
        serializer = self.get_serializer(project)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get all tasks for this project"""
        project = self.get_object()
        tasks = project.tasks.all()
        
        # Apply task filters
        status_filter = request.query_params.get('status')
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        priority_filter = request.query_params.get('priority')
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get project analytics"""
        project = self.get_object()
        
        analytics_data = {
            'total_tasks': project.task_count,
            'completed_tasks': project.completed_task_count,
            'progress_percentage': project.progress_percentage,
            'overdue_tasks': project.tasks.filter(
                due_date__lt=timezone.now(),
                status__in=['todo', 'in_progress']
            ).count(),
            'tasks_by_priority': {
                priority: project.tasks.filter(priority=priority).count()
                for priority in ['low', 'medium', 'high', 'urgent']
            },
            'tasks_by_status': {
                status: project.tasks.filter(status=status).count()
                for status in ['todo', 'in_progress', 'completed', 'cancelled']
            }
        }
        
        return Response(analytics_data)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for tasks - enhanced with Open Linguify-inspired features"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user, active=True)
        
        # Filter by project
        project = self.request.query_params.get('project')
        if project:
            queryset = queryset.filter(project_id=project)
        
        # Filter by personal stage
        stage = self.request.query_params.get('stage')
        if stage:
            queryset = queryset.filter(personal_stage_type_id=stage)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by state (Open Linguify style)
        state_filter = self.request.query_params.get('state')
        if state_filter:
            queryset = queryset.filter(state=state_filter)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by due date
        due_today = self.request.query_params.get('due_today')
        if due_today == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(due_date__date=today)
        
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            queryset = queryset.filter(
                due_date__lt=timezone.now(),
                state__in=['1_todo', '1_in_progress']
            )
        
        # Filter by tags
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__id__in=tag_list).distinct()
        
        # Filter important tasks (starred)
        important_only = self.request.query_params.get('important')
        if important_only == 'true':
            queryset = queryset.filter(priority='1')  # Open Linguify style starred
        
        # Filter closed/open tasks
        open_tasks = self.request.query_params.get('open_tasks')
        if open_tasks == 'true':
            queryset = queryset.exclude(state__in=['1_done', '1_canceled'])
        
        closed_tasks = self.request.query_params.get('closed_tasks')
        if closed_tasks == 'true':
            queryset = queryset.filter(state__in=['1_done', '1_canceled'])
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'kanban':
            return TaskKanbanSerializer
        elif self.action == 'quick_create':
            return TaskQuickCreateSerializer
        elif self.action in ['toggle_state', 'toggle_completed']:
            return TaskToggleSerializer
        return TaskDetailSerializer
    
    def perform_create(self, serializer):
        # Ensure onboarding todo exists for new users
        Task.ensure_onboarding_todo(self.request.user)
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_completed(self, request, pk=None):
        """Toggle task completion status - Open Linguify style"""
        task = self.get_object()
        task.toggle_state()
        
        serializer = TaskToggleSerializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_state(self, request, pk=None):
        """Toggle task state - Open Linguify done checkmark style"""
        task = self.get_object()
        task.toggle_state()
        
        serializer = TaskToggleSerializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_important(self, request, pk=None):
        """Toggle task starred/important status - Open Linguify style"""
        task = self.get_object()
        task.priority = '1' if task.priority == '0' else '0'
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a completed task - move to Archive stage"""
        task = self.get_object()
        
        # Ensure task is completed before archiving
        if task.state != '1_done':
            return Response({
                'error': 'Seules les tâches complétées peuvent être archivées'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find or create Archive stage for user
        archive_stage = task.user.personal_stages.filter(name='Archive').first()
        if not archive_stage:
            # Create Archive stage if it doesn't exist
            max_sequence = task.user.personal_stages.aggregate(
                max_seq=Max('sequence')
            )['max_seq'] or 0
            
            archive_stage = PersonalStageType.objects.create(
                user=task.user,
                name='Archive',
                sequence=max_sequence + 1,
                color='#6f42c1',
                is_closed=True,
                fold=True
            )
        
        # Move task to Archive stage
        task.personal_stage_type = archive_stage
        task.save()
        
        return Response({
            'success': True,
            'message': 'Tâche archivée avec succès',
            'archive_stage_id': str(archive_stage.id),
            'task': TaskListSerializer(task).data
        })
    
    @action(detail=False, methods=['post'])
    def quick_create(self, request):
        """Quick create task - Open Linguify kanban style"""
        serializer = TaskQuickCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            task = serializer.save()
            response_serializer = TaskListSerializer(task)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def kanban(self, request):
        """Kanban view data - grouped by personal stages"""
        tasks = self.get_queryset()
        stages = PersonalStageType.objects.filter(user=request.user).order_by('sequence')
        
        kanban_data = {}
        for stage in stages:
            stage_tasks = tasks.filter(personal_stage_type=stage).order_by('sequence', '-created_at')
            kanban_data[str(stage.id)] = {
                'stage': PersonalStageTypeSerializer(stage).data,
                'tasks': TaskKanbanSerializer(stage_tasks, many=True).data
            }
        
        return Response(kanban_data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard statistics - Open Linguify inspired"""
        user = request.user
        tasks = self.get_queryset()
        
        # Basic stats
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(state='1_done').count()
        starred_tasks = tasks.filter(priority='1').count()
        
        # Due date stats
        today = timezone.now().date()
        due_today = tasks.filter(due_date__date=today).count()
        overdue = tasks.filter(
            due_date__lt=timezone.now(),
            state__in=['1_todo', '1_in_progress']
        ).count()
        
        # Stage breakdown
        stages = PersonalStageType.objects.filter(user=user)
        by_stage = {}
        for stage in stages:
            by_stage[stage.name] = tasks.filter(personal_stage_type=stage).count()
        
        # Priority breakdown  
        by_priority = {
            'normal': tasks.filter(priority='0').count(),
            'starred': tasks.filter(priority='1').count(),
        }
        
        # Recent activity
        recent_completed = tasks.filter(
            state='1_done',
            completed_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        recent_created = tasks.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        activity = {
            'tasks_completed_this_week': recent_completed,
            'tasks_created_this_week': recent_created,
        }
        
        # Quick access
        important_tasks = tasks.filter(priority='1', state__in=['1_todo', '1_in_progress'])[:5]
        upcoming_tasks = tasks.filter(
            due_date__gte=timezone.now(),
            due_date__lte=timezone.now() + timedelta(days=7),
            state__in=['1_todo', '1_in_progress']
        ).order_by('due_date')[:5]
        
        quick_access = {
            'important_tasks': TaskListSerializer(important_tasks, many=True).data,
            'upcoming_tasks': TaskListSerializer(upcoming_tasks, many=True).data,
        }
        
        stats_data = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'due_today': due_today,
            'overdue': overdue,
            'important': starred_tasks,
            'by_stage': by_stage,
            'by_priority': by_priority,
            'activity': activity,
            'quick_access': quick_access,
        }
        
        serializer = DashboardStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get tasks due today"""
        today = timezone.now().date()
        tasks = self.get_queryset().filter(due_date__date=today)
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks"""
        tasks = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        )
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming tasks (next 7 days)"""
        end_date = timezone.now() + timedelta(days=7)
        tasks = self.get_queryset().filter(
            due_date__gte=timezone.now(),
            due_date__lte=end_date,
            status__in=['todo', 'in_progress']
        )
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user)
        
        # Filter by project
        project = self.request.query_params.get('project')
        if project:
            queryset = queryset.filter(project_id=project)
        
        # Filter by task
        task = self.request.query_params.get('task')
        if task:
            queryset = queryset.filter(task_id=task)
        
        # Filter by tags
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__id__in=tag_list).distinct()
        
        # Filter favorites
        favorites_only = self.request.query_params.get('favorites')
        if favorites_only == 'true':
            queryset = queryset.filter(is_favorite=True)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle note favorite status"""
        note = self.get_object()
        note.is_favorite = not note.is_favorite
        note.save()
        
        serializer = self.get_serializer(note)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_pinned(self, request, pk=None):
        """Toggle note pinned status"""
        note = self.get_object()
        note.is_pinned = not note.is_pinned
        note.save()
        
        serializer = self.get_serializer(note)
        return Response(serializer.data)


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming reminders"""
        upcoming_reminders = self.get_queryset().filter(
            remind_at__gte=timezone.now(),
            is_sent=False
        ).order_by('remind_at')[:10]
        
        serializer = self.get_serializer(upcoming_reminders, many=True)
        return Response(serializer.data)


class TaskTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = TaskTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = TaskTemplate.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        )
        
        # Filter public templates only
        public_only = self.request.query_params.get('public')
        if public_only == 'true':
            queryset = queryset.filter(is_public=True)
        
        # Filter featured templates
        featured_only = self.request.query_params.get('featured')
        if featured_only == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Create tasks/project from template"""
        template = self.get_object()
        
        # Increment usage count
        template.usage_count += 1
        template.save()
        
        # Here you would implement the logic to create tasks/projects from template
        # For now, just return success
        return Response({
            'message': 'Template applied successfully',
            'template_id': template.id
        })
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured templates"""
        featured_templates = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_templates, many=True)
        return Response(serializer.data)


# HTMX Views for Todo
class TaskToggleHTMXView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX endpoint for toggling task completion"""
    htmx_template_name = 'todo/partials/task_card.html'
    
    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, user=request.user)
        
        # Toggle completion
        if task.state == '1_done':
            task.state = '1_todo'
            task.completed_at = None
        else:
            task.state = '1_done'
            task.completed_at = timezone.now()
        
        task.save()
        
        context = {'task': task}
        return self.render_htmx_response(context)


class TaskMoveHTMXView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX endpoint for moving tasks between stages"""
    htmx_template_name = 'todo/partials/task_card.html'
    
    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, user=request.user)
        new_stage_id = request.POST.get('stage_id')
        new_position = request.POST.get('position', 0)
        
        if new_stage_id:
            new_stage = get_object_or_404(PersonalStageType, id=new_stage_id, user=request.user)
            task.personal_stage_type = new_stage
            task.sequence = int(new_position)
            task.save()
        
        context = {'task': task}
        return self.render_htmx_response(context)


class TaskQuickCreateHTMXView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX endpoint for quick task creation"""
    htmx_template_name = 'todo/partials/task_card.html'
    
    def post(self, request):
        title = request.POST.get('title', '').strip()
        stage_id = request.POST.get('stage_id')
        
        if not title:
            return HttpResponse('<div class="text-red-500">Title is required</div>')
        
        stage = get_object_or_404(PersonalStageType, id=stage_id, user=request.user) if stage_id else None
        
        # Get default stage if none provided
        if not stage:
            stage = PersonalStageType.objects.filter(user=request.user).first()
            if not stage:
                PersonalStageType.create_default_stages(request.user)
                stage = PersonalStageType.objects.filter(user=request.user).first()
        
        task = Task.objects.create(
            user=request.user,
            title=title,
            personal_stage_type=stage,
            state='1_todo'
        )
        
        context = {'task': task}
        return self.render_htmx_response(context)


class TaskDeleteHTMXView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX endpoint for deleting tasks"""
    
    def delete(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.delete()
        return HttpResponse('')  # Empty response removes element


class TaskListTableHTMXView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX endpoint for task list table with search/filter"""
    htmx_template_name = 'todo/partials/task_list_table.html'
    
    def get(self, request):
        user = request.user
        search_query = request.GET.get('search', '').strip()
        filter_stage = request.GET.get('stage', '')
        filter_project = request.GET.get('project', '')
        filter_priority = request.GET.get('priority', '')
        
        # Base queryset
        tasks = Task.objects.filter(user=user, active=True)
        
        # Apply filters
        if search_query:
            tasks = tasks.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if filter_stage:
            tasks = tasks.filter(personal_stage_type_id=filter_stage)
        
        if filter_project:
            tasks = tasks.filter(project_id=filter_project)
            
        if filter_priority:
            tasks = tasks.filter(priority=filter_priority)
        
        tasks = tasks.order_by('-created_at')
        
        context = {
            'tasks': tasks,
            'search_query': search_query,
            'filters': {
                'stage': filter_stage,
                'project': filter_project,
                'priority': filter_priority,
            }
        }
        return self.render_htmx_response(context)


class KanbanColumnHTMXView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX endpoint for refreshing kanban columns"""
    htmx_template_name = 'todo/partials/kanban_column.html'
    
    def get(self, request, stage_id=None):
        user = request.user
        
        if stage_id:
            stage = get_object_or_404(PersonalStageType, id=stage_id, user=user)
            stages = [stage]
        else:
            stages = PersonalStageType.objects.filter(user=user).order_by('sequence')
        
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
        
        context = {
            'kanban_data': kanban_data,
            'stages': stages
        }
        return self.render_htmx_response(context)


class TaskFormModalHTMXView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX endpoint for task form modal"""
    htmx_template_name = 'todo/partials/task_form_modal.html'
    
    def get(self, request, task_id=None):
        task = None
        if task_id:
            task = get_object_or_404(Task, id=task_id, user=request.user)
        
        context = {
            'task': task,
            'stages': PersonalStageType.objects.filter(user=request.user).order_by('sequence'),
            'projects': Project.objects.filter(user=request.user, status='active'),
            'categories': Category.objects.filter(user=request.user),
            'tags': Tag.objects.filter(user=request.user)
        }
        return self.render_htmx_response(context)
    
    def post(self, request, task_id=None):
        task = None
        if task_id:
            task = get_object_or_404(Task, id=task_id, user=request.user)
        
        # Process form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        stage_id = request.POST.get('stage_id')
        project_id = request.POST.get('project_id')
        category_id = request.POST.get('category_id')
        priority = request.POST.get('priority', 'medium')
        due_date = request.POST.get('due_date')
        
        if not title:
            return HttpResponse('<div class="text-red-500">Title is required</div>')
        
        # Get related objects
        stage = get_object_or_404(PersonalStageType, id=stage_id, user=request.user) if stage_id else None
        project = get_object_or_404(Project, id=project_id, user=request.user) if project_id else None
        category = get_object_or_404(Category, id=category_id, user=request.user) if category_id else None
        
        # Create or update task
        if task:
            task.title = title
            task.description = description
            task.personal_stage_type = stage
            task.project = project
            task.category = category
            task.priority = priority
            if due_date:
                task.due_date = due_date
            task.save()
        else:
            task = Task.objects.create(
                user=request.user,
                title=title,
                description=description,
                personal_stage_type=stage,
                project=project,
                category=category,
                priority=priority,
                due_date=due_date if due_date else None,
                state='1_todo'
            )
        
        # Return updated task card and close modal
        context = {'task': task}
        html = render_to_string('todo/partials/task_card.html', context, request=request)
        return HttpResponse(f'''
            <div hx-swap-oob="outerHTML:#task-{task.id}">{html}</div>
            <script>document.getElementById('task-modal').classList.add('hidden');</script>
        ''')


class StageDeleteHTMXView(LoginRequiredMixin, HTMXResponseMixin, TemplateView):
    """HTMX endpoint for deleting stages"""
    
    def delete(self, request, stage_id):
        stage = get_object_or_404(PersonalStageType, id=stage_id, user=request.user)
        
        # Don't allow deletion if stage has tasks
        if Task.objects.filter(personal_stage_type=stage, active=True).exists():
            return HttpResponse('<div class="text-red-500">Cannot delete stage with active tasks</div>')
        
        stage.delete()
        return HttpResponse('')  # Empty response removes element