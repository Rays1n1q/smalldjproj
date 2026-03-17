from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Announcement, Response, Profile

# Кастомный класс для User, чтобы показывать больше полей в списке
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',              # ← добавили email
        'first_name',         # ← имя
        'last_name',          # ← фамилия
        'is_staff',
        'is_active',
        'date_joined',
    )
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

# Убираем старую регистрацию User и регистрируем нашу кастомную
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Твои остальные модели (оставь как есть или добавь)
admin.site.register(Announcement)
admin.site.register(Response)
admin.site.register(Profile)