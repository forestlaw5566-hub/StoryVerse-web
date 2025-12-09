from django.contrib.auth import update_session_auth_hash, login, authenticate, logout
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import Story, Episode, Category, Comment, Profile, Favorite, Follow
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages


def home(request):
    stories = Story.objects.order_by('-created_at')[:12]
    return render(request, 'core/home.html', {'stories': stories})


from .models import Story, Favorite

def story_detail(request, story_slug):
    story = get_object_or_404(Story, slug=story_slug)

    episodes = story.episodes.all()

    prev_story = Story.objects.filter(id__lt=story.id).order_by('-id').first()
    next_story = Story.objects.filter(id__gt=story.id).order_by('id').first()

    # Verificar si la historia está marcada como favorita
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, story=story).exists()

    context = {
        'story': story,
        'episodes': episodes,
        'prev_story': prev_story,
        'next_story': next_story,
        'is_favorite': is_favorite,
    }

    return render(request, 'core/story_detail.html', context)


def episode_detail(request, story_slug, number):
    story = get_object_or_404(Story, slug=story_slug)
    episode = get_object_or_404(Episode, story=story, number=number)
    comments = Comment.objects.filter(episode=episode).order_by('-created_at')

    # Buscar episodio anterior
    prev_episode = Episode.objects.filter(
        story=story, number__lt=episode.number
    ).order_by('-number').first()

    # Buscar episodio siguiente
    next_episode = Episode.objects.filter(
        story=story, number__gt=episode.number
    ).order_by('number').first()

    if request.method == "POST":
        text = request.POST.get("text")
        if request.user.is_authenticated and text.strip():
            Comment.objects.create(
                user=request.user,
                episode=episode,
                text=text.strip()
            )
            return redirect('episode_detail', story_slug=story_slug, number=number)

    return render(request, 'core/episode_detail.html', {
        'story': story,
        'episode': episode,
        'comments': comments,
        'prev_episode': prev_episode,
        'next_episode': next_episode,
    })


def story_list(request):
    stories = Story.objects.all().order_by('-created_at')
    return render(request, 'core/story_list.html', {'stories': stories})


def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'core/category_list.html', {'categories': categories})


def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    stories = Story.objects.filter(category=category).order_by('-created_at')
    return render(request, 'core/category_detail.html', {
        'category': category,
        'stories': stories,
    })

def search_combined(request):
    query = request.GET.get("q", "").strip()
    stories = Story.objects.filter(title__icontains=query)
    users = User.objects.filter(username__icontains=query)
    return render(request, "core/search_combined.html", {
        "query": query,
        "story_results": stories,
        "user_results": users,
    })


def public_profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    profile = user_obj.profile
    stories = user_obj.story_set.all()

    is_following = False

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user_obj
        ).exists()

    return render(request, "core/public_profile.html", {
        "profile_user": user_obj,
        "profile": profile,
        "stories": stories,
        "is_following": is_following,
    })

@login_required
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)

    # Evitar seguirse a uno mismo
    if target == request.user:
        return redirect("public_profile", username=username)

    follow_obj, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target
    )

    if not created:
        follow_obj.delete()  # dejar de seguir

    return redirect("public_profile", username=username)


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, "core/profile.html", {"profile": profile})

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Datos del usuario
        username = request.POST.get("username")
        email = request.POST.get("email")

        request.user.username = username
        request.user.email = email
        request.user.save()

        # Datos del perfil
        profile.bio = request.POST.get("bio")

        # Avatar
        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]

        profile.save()

        # Redirigir al perfil
        return redirect("profile")

    return render(request, "core/profile_edit.html", {
        "profile": profile
    })


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # no cerrar sesión
            return redirect("profile")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "core/change_password.html", {"form": form})

@login_required
def create_story_view(request):
    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        category_id = request.POST.get("category")
        cover = request.FILES.get("cover")

        if not title or not description:
            return render(request, "core/create_story.html", {
                "categories": categories,
                "error": "El título y la descripción son obligatorios."
            })

        category = Category.objects.get(id=category_id)
        slug = slugify(title)

        story = Story.objects.create(
            title=title,
            description=description,
            category=category,
            cover_image=cover,
            slug=slug,
            author=request.user
        )

        return redirect("author_dashboard")

    return render(request, "core/create_story.html", {
        "categories": categories
    })

@login_required
def author_dashboard(request):
    stories = Story.objects.filter(author=request.user)
    return render(request, "core/author_dashboard.html", {
        "stories": stories
    })

@login_required
def create_episode_view(request, slug):
    story = get_object_or_404(Story, slug=slug)

    # Solo el autor puede publicar capítulos
    if story.author != request.user:
        return render(request, "core/error.html", {
            "message": "No puedes agregar capítulos a una historia que no es tuya."
        })

    if request.method == "POST":
        number = request.POST.get("number")
        title = request.POST.get("title")
        content = request.POST.get("content")

        if not title or not content:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("create_episode", slug=slug)

        Episode.objects.create(
            story=story,
            number=number,
            title=title,
            content=content
        )

        messages.success(request, "Capítulo creado correctamente.")
        return redirect("episode_list", slug=story.slug)

    # Número automático para el siguiente capítulo
    next_number = story.episodes.count() + 1

    return render(request, "core/create_episode.html", {
        "story": story,
        "next_number": next_number
    })

def episode_list_view(request, slug):
    story = get_object_or_404(Story, slug=slug)
    episodes = Episode.objects.filter(story=story).order_by("number")

    return render(request, "core/episode_list.html", {
        "story": story,
        "episodes": episodes
    })

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # inicia sesión automáticamente
            messages.success(request, "Cuenta creada correctamente.")
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "core/register.html", {"form": form})

def login_view(request):

    storage = get_messages(request)
    list(storage)
    storage.used = True

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Credenciales incorrectas.")

    return render(request, "core/login.html")

def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def toggle_favorite(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, story=story)

    if not created:
        fav.delete()
        is_favorite = False
    else:
        is_favorite = True

    # Si es AJAX, devolvemos JSON en vez de redirigir
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"favorite": is_favorite})

    # Si no es AJAX, normal:
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def my_library(request):
    favorites = Favorite.objects.filter(user=request.user).select_related("story")
    return render(request, "core/my_library.html", {"favorites": favorites})

@login_required
def edit_comment(request, comment_id):
    com = get_object_or_404(Comment, id=comment_id)

    if request.user != com.user:
        return redirect('home')

    if request.method == "POST":
        com.text = request.POST.get("text")
        com.save()

        episode = com.episode
        return redirect("episode_detail",
                        story_slug=episode.story.slug,
                        number=episode.number)

    return render(request, "core/edit_comment.html", {"comment": com})


@login_required
def delete_comment(request, comment_id):
    com = get_object_or_404(Comment, id=comment_id)

    if request.user == com.user:
        episode = com.episode
        story = episode.story   # ← AQUÍ SE OBTIENE LA HISTORIA

        com.delete()

        return redirect(
            "episode_detail",
            story_slug=story.slug,
            number=episode.number
        )

    return redirect('home')


@login_required
def send_verification(request):
    user = request.user
    profile = user.profile

    if not user.email:
        messages.error(request, "Debes ingresar un correo en Editar Perfil.")
        return redirect("edit_profile")

    # Generar token de verificación
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verify_url = request.build_absolute_uri(
        reverse("verify_email", args=[uid, token])
    )

    send_mail(
        subject="Verifica tu correo | StoryVerse",
        message=f"Hola, verifica tu correo aquí:\n\n{verify_url}",
        from_email="no-reply@storyverse.com",
        recipient_list=[user.email],
    )

    messages.success(request, "Correo de verificación enviado.")
    return redirect("profile")

@login_required
def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Validar token
    if user is not None and default_token_generator.check_token(user, token):

        profile = user.profile
        profile.email_verified = True
        profile.save()

        messages.success(request, "¡Tu correo fue verificado exitosamente!")
        return redirect("profile")

    # Si el token es incorrecto o expiró
    return render(request, "core/verify_failed.html")

def edit_story(request, story_id):
    story = get_object_or_404(Story, id=story_id, author=request.user)
    categories = Category.objects.all()  # ← NECESARIO

    if request.method == "POST":
        story.title = request.POST.get("title")
        story.description = request.POST.get("description")

        # Guardar categoría seleccionada
        category_id = request.POST.get("category")
        if category_id:
            story.category_id = category_id

        # Guardar nueva portada
        if "cover_image" in request.FILES:
            story.cover_image = request.FILES["cover_image"]

        story.save()
        messages.success(request, "Historia actualizada.")
        return redirect("author_dashboard")
    
    return render(request, "core/edit_story.html", {
        "story": story,
        "categories": categories,   # ← AHORA SÍ
    })


@login_required
def delete_story(request, story_id):
    story = get_object_or_404(Story, id=story_id, author=request.user)
    story.delete()
    messages.success(request, "Historia eliminada.")
    return redirect("author_dashboard")

@login_required
def my_stories(request):
    stories = Story.objects.filter(author=request.user)
    return render(request, "core/author_dashboard.html", {
        "stories": stories
    })

@login_required
def edit_episode(request, episode_id):
    episode = get_object_or_404(Episode, id=episode_id)

    # Solo el autor puede editar
    if episode.story.author != request.user:
        messages.error(request, "No puedes editar capítulos que no son tuyos.")
        return redirect("author_dashboard")

    if request.method == "POST":
        episode.title = request.POST.get("title")
        episode.number = request.POST.get("number")
        episode.content = request.POST.get("content")
        episode.save()

        messages.success(request, "Capítulo actualizado correctamente.")
        return redirect("episode_list", slug=episode.story.slug)

    return render(request, "core/edit_episode.html", {
        "episode": episode
    })

@login_required
def delete_episode(request, episode_id):
    episode = get_object_or_404(Episode, id=episode_id)

    if episode.story.author != request.user:
        messages.error(request, "No puedes eliminar capítulos que no son tuyos.")
        return redirect("author_dashboard")

    story_slug = episode.story.slug
    episode.delete()

    messages.success(request, "Capítulo eliminado correctamente.")
    return redirect("episode_list", slug=story_slug)
