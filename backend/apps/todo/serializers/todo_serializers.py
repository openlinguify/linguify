from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Project, Task, Note, Category, Tag, Reminder, TaskTemplate, PersonalStageType

User = get_user_model()


class PersonalStageTypeSerializer(serializers.ModelSerializer):
    """Serializer for personal stage types - Open Linguify inspired"""
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PersonalStageType
        fields = ['id', 'name', 'sequence', 'fold', 'color', 'is_closed', 'task_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_task_count(self, obj):
        try:
            return obj.tasks.filter(active=True).count()
        except Exception as e:
            # Log the specific error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting task count for stage {obj.name}: {e}")
            # Fallback if tasks relationship is not available
            from ..models import Task
            return Task.objects.filter(personal_stage_type=obj, user=obj.user, active=True).count()
    
    def validate_name(self, value):
        """Validate stage name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom du stage ne peut pas être vide.")
        return value.strip()
    
    def update(self, instance, validated_data):
        """Override update with logging"""
        import logging
        logger = logging.getLogger(__name__)
        try:
            logger.info(f"Updating stage {instance.name} with data: {validated_data}")
            return super().update(instance, validated_data)
        except Exception as e:
            logger.error(f"Error in PersonalStageTypeSerializer.update: {e}", exc_info=True)
            raise


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'icon', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProjectListSerializer(serializers.ModelSerializer):
    """Simplified serializer for project lists"""
    task_count = serializers.ReadOnlyField()
    completed_task_count = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status', 'progress_percentage',
            'due_date', 'is_favorite', 'task_count', 'completed_task_count',
            'category_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'progress_percentage', 'created_at', 'updated_at']


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for project details"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    task_count = serializers.ReadOnlyField()
    completed_task_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'category', 'category_id', 'status',
            'default_view', 'start_date', 'due_date', 'progress_percentage',
            'is_shared', 'is_favorite', 'task_count', 'completed_task_count',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'progress_percentage', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        project = Project.objects.create(**validated_data)
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id, user=project.user)
                project.category = category
                project.save()
            except Category.DoesNotExist:
                pass
        
        return project
    
    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id, user=instance.user)
                validated_data['category'] = category
            except Category.DoesNotExist:
                validated_data['category'] = None
        
        return super().update(instance, validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Simplified serializer for task lists - Open Linguify inspired"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    personal_stage_type = PersonalStageTypeSerializer(read_only=True)
    subtask_count = serializers.ReadOnlyField()
    completed_subtask_count = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    is_closed = serializers.ReadOnlyField()
    name_with_subtask_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'state', 'priority', 'color', 'sequence',
            'progress_percentage', 'due_date', 'is_important', 'is_overdue', 
            'is_closed', 'active', 'project_name', 'personal_stage_type',
            'tags', 'subtask_count', 'completed_subtask_count', 
            'name_with_subtask_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for task details - Open Linguify inspired"""
    project = ProjectListSerializer(read_only=True)
    project_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    parent_task = TaskListSerializer(read_only=True)
    parent_task_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    personal_stage_type = PersonalStageTypeSerializer(read_only=True)
    personal_stage_type_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    subtasks = TaskListSerializer(many=True, read_only=True)
    subtask_count = serializers.ReadOnlyField()
    completed_subtask_count = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    is_closed = serializers.ReadOnlyField()
    name_with_subtask_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'state', 'priority', 'color',
            'sequence', 'progress_percentage', 'project', 'project_id', 
            'parent_task', 'parent_task_id', 'personal_stage_type', 'personal_stage_type_id',
            'tags', 'tag_ids', 'order', 'due_date', 'start_date',
            'estimated_time', 'actual_time', 'is_important', 'is_recurring',
            'reminder_set', 'active', 'is_overdue', 'is_closed', 'subtasks', 
            'subtask_count', 'completed_subtask_count', 'name_with_subtask_count',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        """Validate title length with custom error message"""
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters.")
        return value
    
    def create(self, validated_data):
        project_id = validated_data.pop('project_id', None)
        parent_task_id = validated_data.pop('parent_task_id', None)
        personal_stage_type_id = validated_data.pop('personal_stage_type_id', None)
        tag_ids = validated_data.pop('tag_ids', [])
        
        task = Task.objects.create(**validated_data)
        
        # Set project
        if project_id:
            try:
                project = Project.objects.get(id=project_id, user=task.user)
                task.project = project
                task.save()
            except Project.DoesNotExist:
                pass
        
        # Set parent task
        if parent_task_id:
            try:
                parent_task = Task.objects.get(id=parent_task_id, user=task.user)
                task.parent_task = parent_task
                task.save()
            except Task.DoesNotExist:
                pass
        
        # Set personal stage
        if personal_stage_type_id:
            try:
                stage = PersonalStageType.objects.get(id=personal_stage_type_id, user=task.user)
                task.personal_stage_type = stage
                task.save()
            except PersonalStageType.DoesNotExist:
                pass
        
        # Set tags
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids, user=task.user)
            task.tags.set(tags)
        
        return task
    
    def update(self, instance, validated_data):
        project_id = validated_data.pop('project_id', None)
        parent_task_id = validated_data.pop('parent_task_id', None)
        personal_stage_type_id = validated_data.pop('personal_stage_type_id', None)
        tag_ids = validated_data.pop('tag_ids', None)
        
        # Update project
        if project_id:
            try:
                project = Project.objects.get(id=project_id, user=instance.user)
                validated_data['project'] = project
            except Project.DoesNotExist:
                validated_data['project'] = None
        
        # Update parent task
        if parent_task_id:
            try:
                parent_task = Task.objects.get(id=parent_task_id, user=instance.user)
                validated_data['parent_task'] = parent_task
            except Task.DoesNotExist:
                validated_data['parent_task'] = None
        
        # Update personal stage
        if personal_stage_type_id:
            try:
                stage = PersonalStageType.objects.get(id=personal_stage_type_id, user=instance.user)
                validated_data['personal_stage_type'] = stage
            except PersonalStageType.DoesNotExist:
                validated_data['personal_stage_type'] = None
        
        # Update tags
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids, user=instance.user)
            instance.tags.set(tags)
        
        return super().update(instance, validated_data)


class NoteSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    project_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    task = TaskListSerializer(read_only=True)
    task_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'content_type', 'project', 'project_id',
            'task', 'task_id', 'tags', 'tag_ids', 'is_favorite', 'is_pinned',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        project_id = validated_data.pop('project_id', None)
        task_id = validated_data.pop('task_id', None)
        tag_ids = validated_data.pop('tag_ids', [])
        
        note = Note.objects.create(**validated_data)
        
        # Set project
        if project_id:
            try:
                project = Project.objects.get(id=project_id, user=note.user)
                note.project = project
                note.save()
            except Project.DoesNotExist:
                pass
        
        # Set task
        if task_id:
            try:
                task = Task.objects.get(id=task_id, user=note.user)
                note.task = task
                note.save()
            except Task.DoesNotExist:
                pass
        
        # Set tags
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids, user=note.user)
            note.tags.set(tags)
        
        return note


class ReminderSerializer(serializers.ModelSerializer):
    task = TaskListSerializer(read_only=True)
    task_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    project = ProjectListSerializer(read_only=True)
    project_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'title', 'message', 'reminder_type', 'remind_at',
            'task', 'task_id', 'project', 'project_id', 'is_sent',
            'sent_at', 'created_at'
        ]
        read_only_fields = ['id', 'is_sent', 'sent_at', 'created_at']
    
    def create(self, validated_data):
        task_id = validated_data.pop('task_id', None)
        project_id = validated_data.pop('project_id', None)
        
        reminder = Reminder.objects.create(**validated_data)
        
        # Set task
        if task_id:
            try:
                task = Task.objects.get(id=task_id, user=reminder.user)
                reminder.task = task
                reminder.save()
            except Task.DoesNotExist:
                pass
        
        # Set project
        if project_id:
            try:
                project = Project.objects.get(id=project_id, user=reminder.user)
                reminder.project = project
                reminder.save()
            except Project.DoesNotExist:
                pass
        
        return reminder


class TaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = [
            'id', 'name', 'description', 'template_data', 'is_public',
            'is_featured', 'usage_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at', 'updated_at']


# Open Linguify-inspired specialized serializers

class TaskKanbanSerializer(serializers.ModelSerializer):
    """Kanban-specific serializer for tasks - optimized for kanban view"""
    tags = TagSerializer(many=True, read_only=True)
    personal_stage_type = PersonalStageTypeSerializer(read_only=True)
    subtask_count = serializers.ReadOnlyField()
    name_with_subtask_count = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'name_with_subtask_count', 'description', 'state', 
            'priority', 'color', 'sequence', 'due_date', 'is_important',
            'is_overdue', 'active', 'personal_stage_type', 'tags', 'subtask_count'
        ]
        read_only_fields = ['id']


class TaskQuickCreateSerializer(serializers.ModelSerializer):
    """Quick create serializer for tasks - Open Linguify inspired"""
    
    class Meta:
        model = Task
        fields = ['title', 'description']
    
    def validate_title(self, value):
        """Validate title length with custom error message"""
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters.")
        return value
    
    def create(self, validated_data):
        # Auto-set user from request context
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class TaskToggleSerializer(serializers.ModelSerializer):
    """Serializer for toggling task state - Open Linguify done checkmark style"""
    
    class Meta:
        model = Task
        fields = ['id', 'state', 'status', 'completed_at']
        read_only_fields = ['id', 'completed_at']
    
    def update(self, instance, validated_data):
        # Use the toggle_state method for consistent behavior
        if 'state' in validated_data:
            instance.toggle_state()
            return instance
        return super().update(instance, validated_data)


class DashboardStatsSerializer(serializers.Serializer):
    """Dashboard statistics serializer - Open Linguify inspired"""
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    due_today = serializers.IntegerField()
    overdue = serializers.IntegerField()
    important = serializers.IntegerField()
    by_stage = serializers.DictField()
    by_priority = serializers.DictField()
    activity = serializers.DictField()
    quick_access = serializers.DictField()