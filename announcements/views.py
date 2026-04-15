from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin   # ← добавь
from django.contrib.auth import login, authenticate, logout
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib import messages

from .models import Announcement, Response, Profile
from .forms import CustomUserCreationForm, ResponseForm, ProfileForm
from django.contrib.auth.models import User
from django.views.generic import UpdateView
from django.urls import reverse_lazy

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
    paginate_by = 9  # ← сколько объявлений на странице

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

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

from django.contrib.auth.mixins import LoginRequiredMixin

class MyAnnouncementsView(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'my_announcements.html'
    context_object_name = 'announcements'
    ordering = ['-created_at']

    def get_queryset(self):
        return Announcement.objects.filter(owner=self.request.user)


# ====================== МОИ ОТКЛИКИ ======================
class MyResponsesView(LoginRequiredMixin, ListView):
    model = Response
    template_name = 'my_responses.html'
    context_object_name = 'responses'
    ordering = ['-created_at']

    def get_queryset(self):
        return Response.objects.filter(user=self.request.user)
    


class AnnouncementUpdateView(LoginRequiredMixin, UpdateView):
    model = Announcement
    template_name = 'announcement_edit.html'
    fields = ['title', 'description']
    success_url = reverse_lazy('my_announcements')

    def get_queryset(self):
        # ← Важная защита!
        return Announcement.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['announcement'] = self.object
        return context
    
@login_required
def delete_response(request, response_id):
    response = get_object_or_404(Response, id=response_id)
    
    # Можно удалять только свой отклик
    if response.user == request.user:
        response.delete()
        messages.success(request, "Ваш отклик удалён.")
    else:
        messages.error(request, "Вы не можете удалить этот отклик.")
    
    return redirect('my_responses')