from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from blog.models import Post
from django.utils import timezone

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('users:profile', username=user.username)
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration_form.html', {'form': form})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)
    if request.user != user:
        posts = posts.filter(is_published=True, pub_date__lte=timezone.now())
    return render(request, 'users/profile.html', {'profile_user': user, 'posts': posts})


@login_required
def profile_edit(request, username):
    if request.user.username != username:
        return redirect('users:profile', username=username)
    user = request.user
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users:profile', username=user.username)
    else:
        form = UserChangeForm(instance=user)
    return render(request, 'users/profile_edit.html', {'form': form})
