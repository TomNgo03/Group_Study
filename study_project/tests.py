from django.test import TestCase, Client

from django.urls import reverse
from .models import User

# Create your tests here.

########## User Test ###########

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
        
class LogoutUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(email='test@example.com', password='password')
        
    def test_logout_user(self):
        self.client.login(email='test@example.com', password='password')
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse('home'))
        
class RegisterPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.valid_data = {
            'email': 'test@example.com',
            'password1': 'password',
            'password2': 'password'
        }
        self.invalid_data = {
            'email': 'test@example.com',
            'password1': 'password',
            'password2': 'wrong_password'
        }

    def test_register_page(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'study_project/login_register.html')

    def test_register_valid_data(self):
        response = self.client.post(self.register_url, self.valid_data)
        self.assertRedirects(response, reverse('home'))

    def test_register_invalid_data(self):
        response = self.client.post(self.register_url, self.invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'study_project/login_register.html')

############ Room Test #########################

class CreateRoomTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.topic = Topic.objects.create(name='Test Topic')
        self.create_room_url = reverse('create_room')
        self.valid_data = {
            'topic': self.topic.name,
            'name': 'Test Room',
            'description': 'Test Room Description',
        }

    def test_create_room_authenticated_user(self):
        self.client.login(email='test@example.com', password='password')
        response = self.client.post(self.create_room_url, self.valid_data)
        self.assertRedirects(response, reverse('home'))

    def test_create_room_unauthenticated_user(self):
        response = self.client.post(self.create_room_url, self.valid_data)
        self.assertRedirects(response, reverse('login') + '?next=' + self.create_room_url)

    def test_create_room_invalid_data(self):
        self.client.login(email='test@example.com', password='password')
        invalid_data = {'topic': '', 'name': '', 'description': ''}
        response = self.client.post(self.create_room_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'study_project/room_form.html')
        
class UpdateRoomTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.topic = Topic.objects.create(name='Test Topic')
        self.room = Room.objects.create(host=self.user, topic=self.topic, name='Test Room', description='Test Room Description')
        self.update_room_url = reverse('update_room', args=[self.room.pk])
        self.valid_data = {
            'topic': 'Updated Topic',
            'name': 'Updated Room',
            'description': 'Updated Room Description',
        }

    def test_update_room_authenticated_user(self):
        self.client.login(email='test@example.com', password='password')
        response = self.client.post(self.update_room_url, self.valid_data)
        self.assertRedirects(response, reverse('home'))

    def test_update_room_unauthenticated_user(self):
        response = self.client.post(self.update_room_url, self.valid_data)
        self.assertRedirects(response, reverse('login') + '?next=' + self.update_room_url)

    def test_update_room_invalid_data(self):
        self.client.login(email='test@example.com', password='password')
        invalid_data = {'topic': '', 'name': '', 'description': ''}
        response = self.client.post(self.update_room_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'study_project/room_form.html')

    def test_update_room_unauthorized_user(self):
        user2 = User.objects.create_user(email='user2@example.com', password='password')
        self.client.login(email='user2@example.com', password='password')
        response = self.client.post(self.update_room_url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are not allowed to update this room')
        
class DeleteRoomTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.topic = Topic.objects.create(name='Test Topic')
        self.room = Room.objects.create(host=self.user, topic=self.topic, name='Test Room', description='Test Room Description')
        self.delete_room_url = reverse('delete_room', args=[self.room.pk])

    def test_delete_room_authenticated_user(self):
        self.client.login(email='test@example.com', password='password')
        response = self.client.post(self.delete_room_url)
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(Room.objects.filter(pk=self.room.pk).exists())

    def test_delete_room_unauthenticated_user(self):
        response = self.client.post(self.delete_room_url)
        self.assertRedirects(response, reverse('login') + '?next=' + self.delete_room_url)
        self.assertTrue(Room.objects.filter(pk=self.room.pk).exists())

    def test_delete_room_unauthorized_user(self):
        user2 = User.objects.create_user(email='user2@example.com', password='password')
        self.client.login(email='user2@example.com', password='password')
        response = self.client.post(self.delete_room_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are not allowed to delete this room')
        self.assertTrue(Room.objects.filter(pk=self.room.pk).exists())