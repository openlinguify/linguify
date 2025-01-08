from rest_framework import serializers
from .models import Note, NoteCategory, Tag, SharedNote

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

    def create(self, validated_data):
        user = self.context['request'].user
        return Tag.objects.create(user=user, **validated_data)
    
class NoteCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    notes_count = serializers.SerializerMethodField()

    class Meta:
        model = NoteCategory
        fields = ['id', 'name', 'description', 'parent', 'language',
                 'created_at', 'subcategories', 'notes_count']

    def get_subcategories(self, obj):
        subcategories = NoteCategory.objects.filter(parent=obj)
        return NoteCategorySerializer(subcategories, many=True).data

    def get_notes_count(self, obj):
        return obj.note_set.count()

    def create(self, validated_data):
        user = self.context['request'].user
        return NoteCategory.objects.create(user=user, **validated_data)

class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    needs_review = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'category', 'category_name', 'tags',
            'language', 'note_type', 'created_at', 'updated_at',
            'last_reviewed', 'review_count', 'is_pinned', 'is_archived',
            'priority', 'translation', 'pronunciation', 'example_sentences',
            'difficulty', 'needs_review'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_reviewed', 'review_count']

    def create(self, validated_data):
        tags_data = self.context.get('tags', [])
        user = self.context['request'].user
        note = Note.objects.create(user=user, **validated_data)
        
        if tags_data:
            tags = Tag.objects.filter(id__in=tags_data, user=user)
            note.tags.set(tags)
        
        return note

    def update(self, instance, validated_data):
        tags_data = self.context.get('tags', None)
        note = super().update(instance, validated_data)
        
        if tags_data is not None:
            tags = Tag.objects.filter(id__in=tags_data, user=instance.user)
            note.tags.set(tags)
        
        return note

class SharedNoteSerializer(serializers.ModelSerializer):
    note = NoteSerializer(read_only=True)
    shared_with_username = serializers.CharField(source='shared_with.username', read_only=True)
    
    class Meta:
        model = SharedNote
        fields = ['id', 'note', 'shared_with', 'shared_with_username', 'shared_at', 'can_edit']
        read_only_fields = ['shared_at']

    def create(self, validated_data):
        user = self.context['request'].user
        note_id = self.context.get('note_id')
        note = Note.objects.get(id=note_id, user=user)
        return SharedNote.objects.create(note=note, **validated_data)

class NoteDetailSerializer(NoteSerializer):
    shared_with = SharedNoteSerializer(source='sharednote_set', many=True, read_only=True)
    
    class Meta(NoteSerializer.Meta):
        fields = NoteSerializer.Meta.fields + ['shared_with']