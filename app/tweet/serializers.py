from rest_framework import serializers

from core.models import Tag, Description, Tweet


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class DescriptionSerializer(serializers.ModelSerializer):
    """Serializer for description objects"""

    class Meta:
        model = Description
        fields = ('id', 'name')
        read_only_fields = ('id',)


class TweetSerializer(serializers.ModelSerializer):
    """Serializer a tweet"""
    descriptions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Description.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Tweet
        fields = ('id', 'title', 'descriptions', 'tags')
        read_only_fields = ('id',)


class TweetDetailSerializer(TweetSerializer):
    """Serialize a tweet detail"""
    descriptions = DescriptionSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class TweetImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to tweets"""

    class Meta:
        model = Tweet
        fields = ('id', 'image')
        read_only_fields = ('id',)
