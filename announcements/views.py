from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.generic import ListView, DetailView
from .models import Announcement, Response
from .forms import CustomUserCreationForm, ResponseForm
from django.contrib.auth import authenticate, logout
from django.contrib import messages
from .forms import CustomAuthenticationForm
from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

class HomeView(ListView):
    model = Announcement
    template_name = 'home.html'
    context_object_name = 'announcements'
    ordering = ['-created_at']

@login_required
def create_announcement(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        Announcement.objects.create(title=title, description=description, owner=request.user)
        return redirect('home')
    return render(request, 'create_announcement.html')

class AnnouncementDetailView(DetailView):
    model = Announcement
    template_name = 'announcement_detail.html'
    context_object_name = 'announcement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responses'] = self.object.responses.all()
        context['response_form'] = ResponseForm()
        return context

@login_required
def add_response(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.announcement = announcement
            response.user = request.user
            response.save()
            messages.success(request, "Ваш отклик успешно отправлен!")
            return redirect('home')          # ← сюда редирект на главную
        else:
            messages.error(request, "Проверьте введённые данные")
    
    # Если GET или форма невалидна — остаёмся на странице объявления
    return redirect('announcement_detail', pk=pk)

@login_required
def accept_response(request, response_id):
    response = get_object_or_404(Response, id=response_id)
    if response.announcement.owner == request.user:
        response.status = 'accepted'
        response.save()
    return redirect('announcement_detail', pk=response.announcement.pk)

@login_required
def reject_response(request, response_id):
    response = get_object_or_404(Response, id=response_id)
    if response.announcement.owner == request.user:
        response.status = 'rejected'
        response.save()
    return redirect('announcement_detail', pk=response.announcement.pk)

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Заполните все поля')
        else:
            try:
                user = User.objects.get(email__iexact=email)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    next_url = request.GET.get('next', '/')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Неверный пароль')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден')

    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

from .forms import ProfileForm
from .models import Profile

@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'profile.html', {'form': form, 'profile': profile})

@login_required
def delete_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if announcement.owner != request.user:
        messages.error(request, "Вы не можете удалить чужое объявление")
        return redirect('announcement_detail', pk=pk)
    
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, "Объявление успешно удалено")
        return redirect('home')
    
    # Если GET — показываем подтверждение (опционально, но рекомендуется)
    return render(request, 'announcement_confirm_delete.html', {
        'announcement': announcement
    })