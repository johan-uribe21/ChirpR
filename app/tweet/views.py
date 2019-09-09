from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
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
        elif self.action == 'upload_image':
            return serializers.TweetImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new tweet"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a tweet"""
        tweet = self.get_object()
        serializer = self.get_serializer(
            tweet,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
