from django.test import TestCase
from .models import Movie, MediaItem
from .mixins import DownloadableMixin


class MovieTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie_data = {
            'title': 'Test title',
            'creator': 'Test creator',
            'publication_date': '1999-12-31',
            'duration': 199,
            'format': 'mp4'
        }

    def test_movie_object_creation(self):
        movie = Movie.objects.create(**self.movie_data)

        self.assertIsNotNone(movie.pk)
        self.assertEqual(Movie.objects.count(), 1)

        self.assertEqual(movie.title, 'Test title')
        self.assertEqual(movie.creator, 'Test creator')
        self.assertIsNotNone(movie.publication_date)
        self.assertEqual(movie.duration, 199)
        self.assertEqual(movie.format, 'mp4')

    def test_movie_methods(self):
        movie = Movie.objects.create(**self.movie_data)

        self.assertTrue(hasattr(Movie, 'get_description') and callable(getattr(Movie, 'get_description')))
        self.assertIsNotNone(movie.get_description())

        self.assertTrue(hasattr(Movie, 'play_trailer') and callable(getattr(Movie, 'play_trailer')))
        self.assertIsNotNone(movie.play_trailer())

        self.assertTrue(hasattr(Movie, 'get_media_type') and callable(getattr(Movie, 'get_media_type')))
        self.assertIsNotNone(movie.get_media_type())

    def test_movie_polymorphism(self):
        movie = Movie.objects.create(**self.movie_data)

        self.assertIsInstance(movie, MediaItem)

        self.assertTrue(hasattr(MediaItem, 'get_description'))
        self.assertNotEqual(getattr(Movie, 'get_description'), getattr(MediaItem, 'get_description'))

    def test_movie_mixins_usage(self):
        movie = Movie.objects.create(**self.movie_data)

        self.assertIsInstance(movie, DownloadableMixin)

        self.assertTrue(hasattr(DownloadableMixin, 'download'))
        self.assertEqual(getattr(Movie, 'download'), getattr(DownloadableMixin, 'download'))
