from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from ..models import Project, Task, Note, Category, Tag, Reminder, TaskTemplate, PersonalStageType
from ..serializers import (
    ProjectListSerializer, ProjectDetailSerializer,
    TaskListSerializer, TaskDetailSerializer, TaskKanbanSerializer,
    TaskQuickCreateSerializer, TaskToggleSerializer, DashboardStatsSerializer,
    NoteSerializer, CategorySerializer, TagSerializer,
    ReminderSerializer, TaskTemplateSerializer, PersonalStageTypeSerializer
)


class PersonalStageTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for personal stage types - Open Linguify inspired"""
    serializer_class = PersonalStageTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PersonalStageType.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
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
            stage_tasks = tasks.filter(personal_stage_type=stage)
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