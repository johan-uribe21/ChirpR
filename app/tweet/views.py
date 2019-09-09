from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Description, Tweet
from tweet import serializers


class BaseTweetAttrViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin):
    """Base tweet attribute view set"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new attribute for the authenticated user"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseTweetAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class DescriptionViewSet(BaseTweetAttrViewSet):
    """Manage descriptions in the database"""
    queryset = Description.objects.all()
    serializer_class = serializers.DescriptionSerializer


class TweetViewSet(viewsets.ModelViewSet):
    """Manage tweets in the database"""
    serializer_class = serializers.TweetSerializer
    queryset = Tweet.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the tweets for the authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.TweetDetailSerializer

        return self.serializer_class
