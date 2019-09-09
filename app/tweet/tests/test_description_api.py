from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Description

from tweet.serializers import DescriptionSerializer


DESCRIPTION_URL = reverse('tweet:description-list')


class PublicDescriptionApiTest(TestCase):
    """Test the publicly available description api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(DESCRIPTION_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test ingredients can be retrieved by authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_description_list(self):
        """Test retrieving a list of ingredients"""
        Description.objects.create(user=self.user, name='kale')
        Description.objects.create(user=self.user, name='salt')

        res = self.client.get(DESCRIPTION_URL)

        descriptions = Description.objects.all().order_by('-name')
        serializer = DescriptionSerializer(descriptions, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_descriptions_limited_to_user(self):
        """Test that only ingredients for authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@londonappdev.com',
            'testpass'
        )
        Description.objects.create(user=user2, name='Vinegar')

        description = Description.objects.create(
            user=self.user, name='tumeric')

        res = self.client.get(DESCRIPTION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], description.name)
