from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('team', 'Team / Staff'),
        ('employer', 'Employer'),
        ('candidate', 'Candidate'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, default='Super Admin', blank=True)
    staff_id = models.CharField(max_length=50, blank=True)
    scope = models.CharField(max_length=50, default='all', blank=True)
    phone = models.CharField(max_length=50, blank=True)
    avatar_url = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        username = getattr(self.user, 'username', None) or getattr(self.user, 'email', 'User')
        return f"{username} ({self.role} - {self.department})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            UserProfile.objects.get_or_create(user=instance)
