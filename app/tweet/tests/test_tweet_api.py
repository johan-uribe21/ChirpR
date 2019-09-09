import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tweet, Tag, Description

from tweet.serializers import TweetSerializer, TweetDetailSerializer


TWEET_URL = reverse('tweet:tweet-list')


def image_upload_url(tweet_id):
    """Return URL for tweet image upload"""
    return reverse('tweet:tweet-upload-image', args=[tweet_id])


def detail_url(tweet_id):
    """Return tweet detail url"""
    return reverse('tweet:tweet-detail', args=[tweet_id])


def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_description(user, name='Cinnamon'):
    """Create and return a sample description"""
    return Description.objects.create(user=user,  name=name)


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
        """Test retrieving a list of tweets"""
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

    def test_view_tweet_detail(self):
        """Test viewing a tweet detail"""
        tweet = sample_tweet(user=self.user)
        tweet.tags.add(sample_tag(user=self.user))
        tweet.descriptions.add(sample_description(user=self.user))

        url = detail_url(tweet.id)
        res = self.client.get(url)

        serializer = TweetDetailSerializer(tweet)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_tweet(self):
        """Test creating a tweet"""
        payload = {'title': 'Hello'}
        res = self.client.post(TWEET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tweet = Tweet.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(tweet, key))

    def test_create_tweet_with_tags(self):
        """Test creating a tweet with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(TWEET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tweet = Tweet.objects.get(id=res.data['id'])
        tags = tweet.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_tweet_with_descriptions(self):
        """Test creating a tweet with descriptions"""
        description1 = sample_description(user=self.user, name='Prawn')
        description2 = sample_description(user=self.user, name='Ginger')
        payload = {
            'title': 'Prawn with ginger',
            'descriptions': [description1.id, description2.id]
        }
        res = self.client.post(TWEET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tweet = Tweet.objects.get(id=res.data['id'])
        descriptions = tweet.descriptions.all()
        self.assertEqual(descriptions.count(), 2)
        self.assertIn(description1, descriptions)
        self.assertIn(description1, descriptions)


class TweetImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user@user.com', 'testpass')
        self.client.force_authenticate(self.user)
        self.tweet = sample_tweet(user=self.user)

    def tearDown(self):
        self.tweet.image.delete()

    def test_upload_image_to_tweet(self):
        """Test uploading an image to tweet"""
        url = image_upload_url(self.tweet.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.tweet.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.tweet.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.tweet.id)
        res = self.client.post(url, {'image': 'not image'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
