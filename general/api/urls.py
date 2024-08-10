from rest_framework.routers import SimpleRouter

from general.api.views import UserViewSet, PostViewSet

router = SimpleRouter()
router.register(r'posts', PostViewSet, basename="posts")
router.register(r'users', UserViewSet, basename="users")

urlpatterns = router.urls