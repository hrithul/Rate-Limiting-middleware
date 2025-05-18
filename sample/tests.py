from django.test import TestCase, Client
from django.urls import reverse
import time
from django.core.cache import cache

class RateLimitMiddlewareTest(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_requests_within_limit(self):
        for i in range(5):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn('X-RateLimit-Remaining', response)
            self.assertEqual(int(response['X-RateLimit-Remaining']), 4 - i)

    def test_rate_limit_exceeded(self):
        for i in range(5):
            self.client.get('/')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 429)
        self.assertIn('X-RateLimit-Remaining', response)
        self.assertEqual(int(response['X-RateLimit-Remaining']), 0)
        self.assertJSONEqual(response.content, {'detail': 'Too Many Requests'})

    def test_x_forwarded_for_header(self):
        for i in range(5):
            response = self.client.get('/', HTTP_X_FORWARDED_FOR='1.2.3.4')
            self.assertEqual(response.status_code, 200)
        response = self.client.get('/', HTTP_X_FORWARDED_FOR='1.2.3.4')
        self.assertEqual(response.status_code, 429)
        response = self.client.get('/', HTTP_X_FORWARDED_FOR='5.6.7.8')
        self.assertEqual(response.status_code, 200)
