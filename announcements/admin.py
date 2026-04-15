from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Announcement, Response, Profile


# ====================== КАСТОМНЫЙ USER ======================
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 
                   'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)


# ====================== ANNOUNCEMENT ======================
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at', 'responses_count')
    list_filter = ('created_at', 'owner')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
    raw_id_fields = ('owner',)

    def responses_count(self, obj):
        return obj.responses.count()
    responses_count.short_description = 'Откликов'


# ====================== RESPONSE ======================
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'user', 'status', 'created_at', 'contact')
    list_filter = ('status', 'created_at')
    search_fields = ('message', 'contact', 'user__username', 'announcement__title')
    readonly_fields = ('created_at',)
    raw_id_fields = ('announcement', 'user')


# ====================== PROFILE ======================
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'bio_short')
    search_fields = ('user__username', 'user__email', 'bio')
    raw_id_fields = ('user',)

    def bio_short(self, obj):
        return obj.bio[:80] + "..." if obj.bio and len(obj.bio) > 80 else obj.bio
    bio_short.short_description = 'О себе'


# ====================== РЕГИСТРАЦИЯ ======================
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Profile, ProfileAdmin)