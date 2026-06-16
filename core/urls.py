from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    PlaceViewSet, BorschViewSet, AppUserViewSet,
    CommentViewSet, RatingViewSet, FavoriteBorschViewSet,
    GoogleAuthView,
)

router = DefaultRouter()
router.register(r'places', PlaceViewSet)
router.register(r'borsches', BorschViewSet)
router.register(r'users', AppUserViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'ratings', RatingViewSet)
router.register(r'favorites', FavoriteBorschViewSet)

urlpatterns = [
    path('auth/google/', GoogleAuthView.as_view(), name='auth-google'),
    path('', include(router.urls)),
]
