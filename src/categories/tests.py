from django.test import TestCase

from .models import Category
from playlists.models import Playlist
class CategoryTestCase(TestCase):
    def setUp(self):
        cat_a = Category.objects.create(title='Action')
        cat_b = Category.objects.create(title='Camedy' ,active=False)
        self.play_a = Playlist.objects.create(title='this is my title',
        category=cat_a)
        self.cat_a = cat_a
        self.cat_b = cat_b

    def test_is_active(self):
        self.assertTrue(self.cat_a.active)

    def test_not_is_active(self):
        self.assertFalse(self.cat_b.active)

    def test_related_playlist(self):
        qs = self.cat_a.playlists.all()
        self.assertEqual(qs.count(), 1)

# Create your tests here.
