from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tweet

from tweet.serializers import TweetSerializer


TWEET_URL = reverse('tweet:tweet-list')


def sample_tweet(user, **params):
    """Create a return a sample tweet"""
    defaults = {'title': 'sample tweet'}
    defaults.update(params)

    return Tweet.objects.create(user=user, **defaults)


class PublicTweetApiTest(TestCase):
    """Test unauthenticated tweet API access"""

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test that authentication is required"""
        res = self.client.get(TWEET_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTweetApiTest(TestCase):
    """Test authenticated tweet API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_tweets(self):
        """Test retrieving a list of recipes"""
        sample_tweet(user=self.user)
        sample_tweet(user=self.user)

        res = self.client.get(TWEET_URL)

        tweets = Tweet.objects.all().order_by('-id')
        serializer = TweetSerializer(tweets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tweets_limited_to_user(self):
        """test retrieving tweets for user"""
        user2 = get_user_model().objects.create_user(
            'other@other.com',
            'pass123'
        )
        sample_tweet(user=user2)
        sample_tweet(user=self.user)

        res = self.client.get(TWEET_URL)

        tweets = Tweet.objects.filter(user=self.user)
        serializer = TweetSerializer(tweets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
