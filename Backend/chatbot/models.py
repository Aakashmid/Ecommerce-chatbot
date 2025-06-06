from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatbotSession(models.Model):
    """
    Represents a chatbot conversation session with a user.
    Each session can contain multiple messages.
    """
    SESSION_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatbot_sessions', null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"Session {self.session_id} - {'Guest' if not self.user else self.user.email}"
    
    def end_session(self):
        """End the current session"""
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.save()
    
    @property
    def duration(self):
        """Calculate the duration of the session"""
        end_time = self.ended_at or timezone.now()
        return end_time - self.started_at
    
    @property
    def message_count(self):
        """Get the count of messages in this session"""
        return self.messages.count()


class ChatMessage(models.Model):
    """
    Represents a single message in a chatbot conversation.
    """
    MESSAGE_TYPE = (
        ('user', 'User'),
        ('bot', 'Bot'),
        ('system', 'System'),
    )

    session = models.ForeignKey(ChatbotSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.get_message_type_display()} message in {self.session}"