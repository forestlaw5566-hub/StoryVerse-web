from .models import Category
from .models import Favorite

def categories_nav(request):
    return {
        "categories_nav": Category.objects.all().order_by("name")
    }

def favorite_stories(request):
    if request.user.is_authenticated:
        fav_ids = Favorite.objects.filter(user=request.user).values_list("story_id", flat=True)
        return {"favorite_stories_ids": list(fav_ids)}
    return {"favorite_stories_ids": []}
