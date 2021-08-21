import json

from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import User, Genre, Category, Title
from api.serializers import TitleSerializer

API_PATH = 'http://127.0.0.1:8000/api/v1/'


class Test(APITestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create(username='admin', role=User.ADMIN)
        self.client = APIClient()

    def test_patch_title(self):
        token = RefreshToken.for_user(self.admin)
        self.client.force_authenticate(self.admin, token)
        Genre.objects.create(name='Drama', slug='drama')
        Category.objects.create(name='Movie', slug='movie')
        response = self.client.post('http://localhost:8000/api/v1/titles/',
                                    data={'name': 'lessgo', 'year': 1000, 'genre': ['drama'], 'category': 'movie'})
        response = self.client.patch('http://localhost:8000/api/v1/titles/1/', data={'year': 1002})
        print('lessgo')

    def test_get_reviews(self):
        Genre.objects.create(name='Drama', slug='drama')
        Category.objects.create(name='Movie', slug='movie')
        token = RefreshToken.for_user(self.admin)
        self.client.force_authenticate(self.admin, token)
        response = self.client.post('http://localhost:8000/api/v1/titles/',
                                    data={'name': 'lessgo', 'year': 1000, 'genre': ['drama'], 'category': 'movie'})
        self.client.get('http://localhost:8000/api/v1/titles/1/reviews/')

    def test_pog(self):
        token = RefreshToken.for_user(self.admin)
        self.client.force_authenticate(self.admin, token)
        User.objects.create(username='lessgo')
        response = self.client.get('http://127.0.0.1:8000/api/v1/users/me/')
        sh = json.loads(response.content)
        print('sheesh')

    def test_decorator(self):
        response = self.client.get(API_PATH + 'categories/')
        print('lessgo')
