from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib import messages
from .models import Post, Comment, Follow
from .forms import PostForm, CommentForm  # Tu devras créer ces formulaires
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import PrivateMessage, User, get_follower_count
from .models import Post


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')  # Remplace 'home' par l'URL de ton feed principal
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def home(request):
    posts = Post.objects.all().order_by('-created_at')
    users_with_followers = User.objects.prefetch_related('followers').all()  # Prend en compte les abonnés
    return render(request, 'users/home.html', {'posts': posts, 'users_with_followers': users_with_followers})


User.add_to_class('get_follower_count', get_follower_count)

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Connecte l'utilisateur
            messages.success(request, "Vous êtes connecté avec succès !")  # Message de succès
            return redirect('home')  # Redirige vers la page d'accueil ou un autre feed principal
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# Vue pour le feed principal

def home(request):
    posts = Post.objects.all()  # Vérifiez que cela retourne des publications
    for post in posts:
        print(f'Post ID: {post.id}, Title: {post.title}')  # Debugging
    return render(request, 'users/home.html', {'posts': posts})

def home(request):
    posts = Post.objects.all()  # Assurez-vous que cette ligne fonctionne correctement
    return render(request, 'users/home.html', {'posts': posts})

# Vue pour publier un nouveau post
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            # Envoyer une notification à tous les abonnés
            followers = Follow.objects.filter(followed=post.author)
            for follow in followers:
                PrivateMessage.objects.create(
                    sender=request.user,
                    receiver=follow.follower,
                    content=f"Nouvelle publication de {post.author.username}: {post.content}"
                )

            messages.success(request, "Publication créée avec succès !")
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'users/create_post.html', {'form': form})


# Vue pour commenter un post
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('home')
    else:
        form = CommentForm()
    return render(request, 'users/add_comment.html', {'form': form, 'post': post})

# Vue pour suivre un utilisateur
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
    return redirect('home')

@login_required
def send_message(request, user_id):
    receiver = User.objects.get(id=user_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        PrivateMessage.objects.create(sender=request.user, receiver=receiver, content=content)
        return redirect('view_messages', user_id=receiver.id)
    return render(request, 'users/send_message.html', {'receiver': receiver})


@login_required
def view_messages(request, user_id):
    user = User.objects.get(id=user_id)
    messages = PrivateMessage.objects.filter(
        sender=request.user, receiver=user
    ) | PrivateMessage.objects.filter(
        sender=user, receiver=request.user
    )
    messages = messages.order_by('timestamp')
    return render(request, 'users/view_messages.html', {'messages': messages, 'user': user})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('home')  # Redirige si l'utilisateur n'est pas l'auteur

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Publication mise à jour avec succès !")
            return redirect('home')
    else:
        form = PostForm(instance=post)
    
    return render(request, 'users/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('home')  # Redirige si l'utilisateur n'est pas l'auteur

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Publication supprimée avec succès !")
        return redirect('home')
    
    return render(request, 'users/delete_post.html', {'post': post})

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    
    # Vérifier si l'utilisateur suit le profil
    follow_relation = Follow.objects.filter(follower=request.user, followed=user_to_unfollow).first()
    
    if follow_relation:
        follow_relation.delete()  # Supprimer la relation de suivi

    messages.success(request, f"Vous vous êtes désabonné de {user_to_unfollow.username} !")
    return redirect('home')  # Rediriger vers la page d'accueil ou le feed principal

@login_required
def view_private_messages(request):
    messages = PrivateMessage.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'messages/private_messages.html', {'messages': messages})

@login_required
def received_messages(request):
    # Récupère les messages reçus par l'utilisateur connecté
    messages = PrivateMessage.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'messages/received_messages.html', {'messages': messages})