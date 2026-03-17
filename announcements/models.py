from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Announcement(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_announcements')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Response(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонён'),
    ]
    
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True, verbose_name="Сообщение")
    contact = models.CharField(max_length=100, verbose_name="Контакт (Telegram / телефон)")  # ← НОВОЕ
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('announcement', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.announcement.title}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Возраст")
    bio = models.TextField(blank=True, verbose_name="О себе")

    def __str__(self):
        return self.user.username

# Автосоздание профиля при регистрации
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)