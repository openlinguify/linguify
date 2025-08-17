from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Project, Task, Note, Category, Tag, Reminder, TaskTemplate

User = get_user_model()


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
    """Simplified serializer for task lists"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    subtask_count = serializers.ReadOnlyField()
    completed_subtask_count = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'priority', 'progress_percentage',
            'due_date', 'is_important', 'is_overdue', 'project_name',
            'tags', 'subtask_count', 'completed_subtask_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for task details"""
    project = ProjectListSerializer(read_only=True)
    project_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    parent_task = TaskListSerializer(read_only=True)
    parent_task_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
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
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'progress_percentage',
            'project', 'project_id', 'parent_task', 'parent_task_id',
            'tags', 'tag_ids', 'order', 'due_date', 'start_date',
            'estimated_time', 'actual_time', 'is_important', 'is_recurring',
            'reminder_set', 'is_overdue', 'subtasks', 'subtask_count',
            'completed_subtask_count', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        project_id = validated_data.pop('project_id', None)
        parent_task_id = validated_data.pop('parent_task_id', None)
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
        
        # Set tags
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids, user=task.user)
            task.tags.set(tags)
        
        return task
    
    def update(self, instance, validated_data):
        project_id = validated_data.pop('project_id', None)
        parent_task_id = validated_data.pop('parent_task_id', None)
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