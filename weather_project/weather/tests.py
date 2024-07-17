from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import SearchHistory, UserSearchHistory


class WeatherAppTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')
        self.api_url = reverse('search_history_api')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.search_history_london = SearchHistory.objects.create(city='London', search_count=1)

    def test_index_page_status_code(self):
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)

    def test_post_weather_search(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(self.index_url, {'city': 'London'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'London')
        self.assertContains(response, 'Temperature')
        self.search_history_london.refresh_from_db()
        self.assertEqual(self.search_history_london.search_count, 2)
        self.assertTrue(UserSearchHistory.objects.filter(user=self.user, city='London').exists())

    def test_search_history_model(self):
        self.assertEqual(self.search_history_london.city, 'London')
        self.assertEqual(self.search_history_london.search_count, 1)

    def test_search_history_update(self):
        self.client.post(self.index_url, {'city': 'London'})
        self.search_history_london.refresh_from_db()
        self.assertEqual(self.search_history_london.search_count, 2)

    def test_new_city_search(self):
        response = self.client.post(self.index_url, {'city': 'New York'})
        self.assertEqual(response.status_code, 200)
        new_city = SearchHistory.objects.get(city='New York')
        self.assertEqual(new_city.city, 'New York')
        self.assertEqual(new_city.search_count, 1)

    def test_city_search_case_insensitive(self):
        response = self.client.post(self.index_url, {'city': 'london'})
        self.assertEqual(response.status_code, 200)
        self.search_history_london.refresh_from_db()
        self.assertEqual(self.search_history_london.search_count, 1)

    def test_city_search_russian(self):
        response = self.client.post(self.index_url, {'city': 'Москва'})
        self.assertEqual(response.status_code, 200)
        moscow_history = SearchHistory.objects.get(city='Москва')
        self.assertEqual(moscow_history.city, 'Москва')
        self.assertEqual(moscow_history.search_count, 1)

    def test_city_search_russian_case_insensitive(self):
        response = self.client.post(self.index_url, {'city': 'москва'})
        self.assertEqual(response.status_code, 200)
        moscow_history = SearchHistory.objects.get(city='москва')
        self.assertEqual(moscow_history.city, 'москва')
        self.assertEqual(moscow_history.search_count, 1)

    def test_api_search_history(self):
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('London', data)
        self.assertEqual(data['London'], 1)
