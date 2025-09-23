from apps.authentication.models import User
from django.db import models

import time


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, help_text="Brève description de l'utilisateur")
    learning_languages = models.JSONField(
        blank=True,
        null=True,
        help_text="Langues que l'utilisateur souhaite apprendre, exemple : ['French', 'Spanish']"
    )
    teaching_languages = models.JSONField(
        blank=True,
        null=True,
        help_text="Langues que l'utilisateur peut enseigner, exemple : ['English', 'German']"
    )
    friends = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='friends_with')
    blocked_users = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='blocked_by')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="Photo de profil")
    is_online = models.BooleanField(default=False, help_text="Statut en ligne de l'utilisateur")

    def __str__(self):
        return self.user.username

    def mutual_friends(self, other_user):
        """Renvoie une liste des amis communs avec un autre utilisateur"""
        return self.friends.filter(id__in=other_user.profile.friends.values_list('id', flat=True))

    def friend_requests_sent(self):
        """Renvoie une liste des demandes d'amis envoyées par l'utilisateur"""
        return FriendRequest.objects.filter(sender=self.user)

    def friend_requests_received(self):
        """Renvoie une liste des demandes d'amis reçues par l'utilisateur"""
        return FriendRequest.objects.filter(receiver=self.user)

    def unread_notifications(self):
        """Renvoie une liste des notifications non lues de l'utilisateur"""
        return Notification.objects.filter(recipient=self, is_read=False)

    def unread_messages(self):
        """Renvoie une liste des messages non lus de l'utilisateur"""
        return ChatMessage.objects.filter(receiver=self, is_read=False)

    def unread_group_messages(self):
        return GroupMessage.objects.filter(group__members=self, is_read=False)

    def suggest_friends(self, limit=10):
        """
        Returns intelligent friend suggestions based on multiple factors:
        - Language exchange compatibility (native/target language match)
        - Common friends
        - Similar learning goals
        - Activity level
        """
        from django.db.models import Q, Count, F
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Exclude current friends and self
        excluded_ids = list(self.friends.values_list('id', flat=True)) + [self.id]
        
        # Start with all profiles except excluded
        suggestions = Profile.objects.exclude(id__in=excluded_ids)
        
        # Priority 1: Perfect language exchange match
        # Users whose native language is what I'm learning AND who are learning my native language
        if hasattr(self.user, 'learning_profile'):
            user_learning = self.user.learning_profile
            if user_learning.native_language and user_learning.target_language:
                perfect_matches = suggestions.filter(
                    user__learning_profile__native_language=user_learning.target_language,
                    user__learning_profile__target_language=user_learning.native_language
                )

                # Priority 2: One-way language match
                # Users who speak what I'm learning OR are learning what I speak
                good_matches = suggestions.filter(
                    Q(user__learning_profile__native_language=user_learning.target_language) |
                    Q(user__learning_profile__target_language=user_learning.native_language)
                ).exclude(id__in=perfect_matches.values_list('id', flat=True))

                # Priority 3: Same target language (study buddies)
                study_buddies = suggestions.filter(
                    user__learning_profile__target_language=user_learning.target_language
                ).exclude(
                    id__in=list(perfect_matches.values_list('id', flat=True)) +
                    list(good_matches.values_list('id', flat=True))
                )
            
                # Combine with weights
                from itertools import chain
                weighted_suggestions = list(chain(
                perfect_matches[:limit//2],  # Half of suggestions from perfect matches
                good_matches[:limit//3],      # Third from good matches
                study_buddies[:limit//6]       # Remaining from study buddies
            ))
            
            # If we still need more suggestions, add random active users
            if len(weighted_suggestions) < limit:
                remaining = suggestions.exclude(
                    id__in=[p.id for p in weighted_suggestions]
                ).filter(is_online=True)[:limit - len(weighted_suggestions)]
                weighted_suggestions.extend(remaining)
            
            return weighted_suggestions[:limit]
        
        # Fallback to original logic if user doesn't have language preferences set
        return suggestions.filter(
            Q(learning_languages__overlap=self.teaching_languages) |
            Q(teaching_languages__overlap=self.learning_languages) if self.learning_languages else Q()
        )[:limit]

class Post(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField(null=False, blank=False, max_length=5000, help_text="Post content", verbose_name="Post Content")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='likes_posts', blank=True)
    reposts = models.ManyToManyField(User, related_name='reposts', blank=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='likes_comments', blank=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"

class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10,
                              choices=[('pending', 'pending'), ('accepted', 'accepted'), ('rejected', 'rejected')],
                              default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} sent a friend request to {self.receiver}"

class FriendList(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend_lists')
    name = models.CharField(max_length=100)
    friends = models.ManyToManyField(Profile, related_name='listed_in')

    def __str__(self):
        return f"{self.owner.user.username}'s {self.name}"

class Conversation(models.Model):
    participants = models.ManyToManyField(Profile, related_name='conversations')
    last_message = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation between {', '.join([p.user.username for p in self.participants.all()])}"

class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    media = models.FileField(upload_to='chat/media/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.user.username} -> {self.receiver.user.username} ({self.timestamp})"

LANGUAGE_LEVEL_CHOICES = [
    ('beginner', 'Beginner (A1-A2)'),
    ('intermediate', 'Intermediate (B1-B2)'),
    ('advanced', 'Advanced (C1-C2)'),
    ('mixed', 'Mixed Levels'),
]

GROUP_TYPE_CHOICES = [
    ('conversation', 'Conversation Practice'),
    ('grammar', 'Grammar Study'),
    ('vocabulary', 'Vocabulary Building'),
    ('reading', 'Reading Club'),
    ('writing', 'Writing Practice'),
    ('pronunciation', 'Pronunciation Practice'),
    ('culture', 'Cultural Exchange'),
    ('general', 'General Study'),
]

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True, help_text="Description du groupe")
    avatar = models.ImageField(upload_to='groups/avatars/', blank=True, null=True, help_text="Avatar du groupe")
    language = models.CharField(max_length=10, choices=[
        ('EN', 'English'),
        ('FR', 'French'),
        ('ES', 'Spanish'),
        ('DE', 'German'),
        ('IT', 'Italian'),
        ('PT', 'Portuguese'),
        ('NL', 'Dutch'),
    ], default='EN', help_text="Primary language for this group")
    level = models.CharField(max_length=20, choices=LANGUAGE_LEVEL_CHOICES, default='mixed')
    group_type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES, default='general')
    max_members = models.PositiveIntegerField(default=20, help_text="Maximum number of members")
    is_private = models.BooleanField(default=False, help_text="Private groups require invitation")
    members = models.ManyToManyField(Profile, related_name='groups', blank=True)
    moderators = models.ManyToManyField(Profile, related_name='moderated_groups', blank=True)
    created_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    rules = models.TextField(blank=True, null=True, help_text="Group rules and guidelines")
    activity_level = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
    ], default='medium')
    
    # Language exchange specific fields
    native_speakers_only = models.BooleanField(default=False, help_text="Only allow native speakers")
    requires_language_exchange = models.BooleanField(default=False, help_text="Members must offer language exchange")
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_language_display()})"

    def is_full(self):
        return self.members.count() >= self.max_members

    def can_join(self, user_profile):
        """Check if a user can join this group"""
        if self.is_full():
            return False, "Group is full"
        
        if self.is_private:
            return False, "Group is private - invitation required"
        
        if self.native_speakers_only:
            if user_profile.user.native_language != self.language:
                return False, "Only native speakers allowed"
        
        return True, "Can join"

    def get_activity_score(self):
        """Calculate group activity score based on recent messages"""
        from django.utils import timezone
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=7)
        recent_messages = self.messages.filter(timestamp__gte=week_ago).count()
        
        if recent_messages > 50:
            return 'high'
        elif recent_messages > 10:
            return 'medium'
        else:
            return 'low'

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/icons/')
    awarded_users = models.ManyToManyField(Profile, related_name='badges', blank=True)

    def __str__(self):
        return self.name

class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message in {self.group.name} by {self.sender.user.username}"

class Notification(models.Model):
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notifications')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.user.username}"

class Recommendation(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='recommendations')
    suggested_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='suggested_to')
    reason = models.CharField(max_length=255, blank=True, null=True, help_text="Raison pour cette recommandation")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.profile.user.username} -> {self.suggested_profile.user.username}"

def generate_recommendations(profile):
    """Génère des recommandations d'amis pour un profil."""
    potential_friends = Profile.objects.filter(
        learning_languages__overlap=profile.teaching_languages
    ).exclude(
        id=profile.id
    ).exclude(
        id__in=profile.friends.all()
    )
    for suggested_profile in potential_friends:
        Recommendation.objects.get_or_create(profile=profile, suggested_profile=suggested_profile)

class Story(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='stories')
    content_type = models.CharField(max_length=10, choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video')])
    content = models.TextField(blank=True, null=True)
    media = models.FileField(upload_to='stories/media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Story by {self.profile.user.username}"

    def is_expired(self):
        return self.expires_at < time.now()

class Reputation(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='reputation')
    points = models.IntegerField(default=0)
    level = models.CharField(max_length=50, default='Beginner')

    def update_level(self):
        if self.points >= 1000:
            self.level = 'Expert'
        elif self.points >= 500:
            self.level = 'Intermediate'
        else:
            self.level = 'Beginner'
        self.save()

    def __str__(self):
        return f"{self.profile.user.username} - {self.points} points ({self.level})"

class UserStatistics(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='statistics')
    total_friends = models.IntegerField(default=0)
    total_messages = models.IntegerField(default=0)
    total_help_sessions = models.IntegerField(default=0)

    def __str__(self):
        return f"Stats for {self.profile.user.username}"

class Report(models.Model):
    reported_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reports_filed')
    reported_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reported_by.user.username} against {self.reported_profile.user.username}"

class ActivityFeed(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='activity_feeds')
    activity_type = models.CharField(max_length=50, choices=[
        ('post', 'Post'), 
        ('comment', 'Comment'), 
        ('like', 'Like'),
        ('lesson_completed', 'Lesson Completed'),
        ('friend_added', 'Friend Added'),
        ('group_joined', 'Group Joined'),
        ('achievement', 'Achievement Earned'),
        ('language_exchange', 'Language Exchange Session'),
        ('study_session', 'Study Session'),
    ])
    activity_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Activity for {self.profile.user.username} - {self.activity_type}"

    class Meta:
        ordering = ['-created_at']


class LanguageExchangeSession(models.Model):
    """Model for tracking language exchange sessions between users"""
    participants = models.ManyToManyField(Profile, related_name='exchange_sessions')
    primary_language = models.CharField(max_length=10, default='EN', help_text="Language being taught/practiced")
    secondary_language = models.CharField(max_length=10, default='FR', help_text="Language being learned")
    session_type = models.CharField(max_length=20, choices=[
        ('conversation', 'Conversation Practice'),
        ('correction', 'Text Correction'),
        ('pronunciation', 'Pronunciation Help'),
        ('cultural', 'Cultural Exchange'),
        ('mixed', 'Mixed Practice'),
    ], default='conversation')
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    session_notes = models.TextField(blank=True, help_text="Notes from the session")
    
    # Ratings
    teacher_rating = models.PositiveIntegerField(null=True, blank=True, help_text="Rating for the teacher (1-5)")
    learner_rating = models.PositiveIntegerField(null=True, blank=True, help_text="Rating for the learner (1-5)")
    
    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        participants_str = " & ".join([p.user.username for p in self.participants.all()])
        return f"Exchange: {participants_str} ({self.primary_language}↔{self.secondary_language})"

    def get_duration(self):
        if self.ended_at and self.started_at:
            return (self.ended_at - self.started_at).total_seconds() / 60
        return None


class StudySession(models.Model):
    """Model for group study sessions"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='study_sessions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    max_participants = models.PositiveIntegerField(default=10)
    participants = models.ManyToManyField(Profile, related_name='study_sessions', blank=True)
    created_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='created_study_sessions')
    
    # Session content
    topics = models.JSONField(default=list, help_text="List of topics to cover")
    materials = models.JSONField(default=list, help_text="Study materials and resources")
    
    # Session state
    is_cancelled = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self):
        return f"{self.title} - {self.group.name}"

    def is_full(self):
        return self.participants.count() >= self.max_participants

    def can_join(self, user_profile):
        if self.is_full():
            return False, "Session is full"
        if not self.group.members.filter(id=user_profile.id).exists():
            return False, "Must be a group member"
        return True, "Can join"


class LanguagePartnerMatch(models.Model):
    """Model for tracking language partner matches and compatibility"""
    requester = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='partner_requests')
    partner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='partner_matches')
    
    # Match criteria
    requester_teaches = models.CharField(max_length=10, default='EN', help_text="Language requester can teach")
    requester_learns = models.CharField(max_length=10, default='FR', help_text="Language requester wants to learn")
    partner_teaches = models.CharField(max_length=10, default='FR', help_text="Language partner can teach")
    partner_learns = models.CharField(max_length=10, default='EN', help_text="Language partner wants to learn")
    
    # Match quality
    compatibility_score = models.PositiveIntegerField(default=0, help_text="Match quality score (0-100)")
    is_mutual = models.BooleanField(default=False, help_text="Both users can help each other")
    
    # Match status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ], default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_interaction = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('requester', 'partner')
        ordering = ['-compatibility_score', '-created_at']

    def __str__(self):
        return f"{self.requester.user.username} ↔ {self.partner.user.username} ({self.compatibility_score}%)"

    def calculate_compatibility(self):
        """Calculate compatibility score based on language exchange potential"""
        score = 0
        
        # Perfect mutual exchange (both can teach what the other wants to learn)
        if (self.requester_teaches == self.partner_learns and 
            self.partner_teaches == self.requester_learns):
            score = 100
            self.is_mutual = True
        
        # One-way exchange (requester can teach what partner wants to learn)
        elif self.requester_teaches == self.partner_learns:
            score = 70
        
        # One-way exchange (partner can teach what requester wants to learn)
        elif self.partner_teaches == self.requester_learns:
            score = 70
        
        # Same target language (can practice together)
        elif self.requester_learns == self.partner_learns:
            score = 40
        
        # Same native language (can help with culture/advanced topics)
        elif self.requester_teaches == self.partner_teaches:
            score = 30
        
        self.compatibility_score = score
        return score
