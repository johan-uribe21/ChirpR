from rest_framework import serializers

from core.models import Tag, Description


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
