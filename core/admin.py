from django.contrib import admin
from .models import Category, Story, Episode, Comment, Profile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 0
    fields = ("number", "title", "created_at")
    readonly_fields = ("created_at",)
    ordering = ("number",)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "status", "views", "created_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)
    inlines = [EpisodeInline]

    readonly_fields = ("views", "created_at")

    fieldsets = (
        ("Información General", {
            "fields": ("title", "slug", "description", "author", "category", "status")
        }),
        ("Multimedia", {
            "fields": ("cover_image",)
        }),
        ("Estadísticas", {
            "fields": ("views", "created_at")
        }),
    )


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("story", "number", "title", "created_at")
    search_fields = ("title", "story__title")
    list_filter = ("story",)
    ordering = ("story", "number")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("episode", "user", "created_at")
    search_fields = ("user__username", "episode__title", "text")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio")
