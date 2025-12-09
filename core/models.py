from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


# ===========================
#      CATEGORY
# ===========================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ===========================
#      STORY
# ===========================
class Story(models.Model):
    STATUS_CHOICES = (
        ("draft", "Borrador"),
        ("published", "Publicado"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    cover_image = models.ImageField(upload_to="covers/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historia"
        verbose_name_plural = "Historias"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    # ⭐ NUEVO: Contador usando el modelo Favorite
    def favorites_count(self):
        return self.favorited_by.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"


# ===========================
#      EPISODE
# ===========================
class Episode(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="episodes")
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Episodio"
        verbose_name_plural = "Episodios"
        ordering = ["number"]
        unique_together = ("story", "number")

    def __str__(self):
        return f"{self.story.title} - {self.title}"

# ===========================
#      COMMENT
# ===========================
class Comment(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comentario de {self.user.username}"


# ===========================
#      PROFILE
# ===========================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        upload_to="avatars/",
        default="media/avatars/default.png",
        blank=True,
        null=True
    )
    bio = models.TextField(max_length=300, blank=True)
    email_verified = models.BooleanField(default=False)


    def __str__(self):
        return f"Perfil de {self.user.username}"


# ===========================
#      FAVORITE (Nuevo)
# ===========================
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "story")

    def __str__(self):
        return f"{self.user.username} → {self.story.title}"
