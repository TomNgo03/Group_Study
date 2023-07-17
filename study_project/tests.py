from django.test import TestCase, Client

from django.urls import reverse
from .models import User

# Create your tests here.

class LoginPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(email = 'test@example.com', password = 'password')
    
    def test_login_page(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response, 'study_project/login_register.html')

    def test_login(self):
        response = self.client.post(self.login_url, {'email': 'test@example.com', 'password': 'password'})
        self.assertRedirects(response, reverse('home'))
    
    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {'email': 'test@example.com', 'password': 'wrong_password'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'study_project/login_register.html')
        
        