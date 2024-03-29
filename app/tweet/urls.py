from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tweet import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('descriptions', views.DescriptionViewSet)
router.register('tweets', views.TweetViewSet)

app_name = 'tweet'

urlpatterns = [
    path('', include(router.urls)),
]
