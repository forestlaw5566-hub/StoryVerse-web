from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # HISTORIAS
    path("historias/", views.story_list, name="story_list"),
    path("historia/<slug:story_slug>/", views.story_detail, name="story_detail"),
    path("historia/<slug:story_slug>/episodio/<int:number>/", views.episode_detail, name="episode_detail"),

    # CATEGORÍAS
    path("categorias/", views.category_list, name="category_list"),
    path("categorias/<slug:category_slug>/", views.category_detail, name="category_detail"),

    # BUSCADOR
    path("buscar/", views.search_combined, name="search_combined"),

    # PERFIL
    path("perfil/", views.profile_view, name="profile"),
    path("perfil/editar/", views.edit_profile, name="edit_profile"),
    path("perfil/password/", views.change_password, name="change_password"),

    # CREAR HISTORIAS
    path("historias/crear/", views.create_story_view, name="create_story"),
    path("historias/<slug:slug>/capitulos/crear/", views.create_episode_view, name="create_episode"),
    path("historias/<slug:slug>/capitulos/", views.episode_list_view, name="episode_list"),

    # PANEL
    path("panel/", views.author_dashboard, name="author_dashboard"),

    # AUTH
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # FAVORITOS
    path("favorito/<int:story_id>/", views.toggle_favorite, name="toggle_favorite"),
    path("mi-biblioteca/", views.my_library, name="my_library"),

    # COMENTARIOS
    path("comentario/<int:comment_id>/editar/", views.edit_comment, name="edit_comment"),
    path("comentario/<int:comment_id>/eliminar/", views.delete_comment, name="delete_comment"),

    # VERIFICACIÓN
    path("perfil/verificar/", views.send_verification, name="send_verification"),
    path("perfil/verificar/<uidb64>/<token>/", views.verify_email, name="verify_email"),

    # MIS HISTORIAS
    path("mis-historias/", views.my_stories, name="my_stories"),

    # EDITAR / ELIMINAR
    path("editar-historia/<int:story_id>/", views.edit_story, name="edit_story"),
    path("eliminar-historia/<int:story_id>/", views.delete_story, name="delete_story"),
    path("editar-capitulo/<int:episode_id>/", views.edit_episode, name="edit_episode"),
    path("eliminar-capitulo/<int:episode_id>/", views.delete_episode, name="delete_episode"),

    # PERFILES PÚBLICOS + FOLLOW
    path("usuario/<str:username>/", views.public_profile, name="public_profile"),
    path("seguir/<str:username>/", views.toggle_follow, name="toggle_follow"),
    path("@<str:username>/", views.public_profile, name="public_profile_short"),
]
