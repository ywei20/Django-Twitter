from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User


LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


class AccountApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user(
            username='admin',
            email='admin@gmail.com',
            password='password',
        )

    def create_user(self, username, email, password):
        return User.objects.create_user(username, email, password)

    def test_login(self):
        # test with wrong http method
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'password',
        })
        self.assertEquals(response.status_code, 405)

        # test with correct http method but wrong password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEquals(response.status_code, 400)
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEquals(response.data['has_logged_in'], False)

        # test failure with non-existent username
        response = self.client.post(LOGIN_URL, {
            'username': 'not exist',
            'password': 'password',
        })
        self.assertEquals(response.status_code, 400)
        self.assertEquals(str(response.data['errors']['username'][0]), 'User does not exist.')

        # test login success
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'password',
        })
        self.assertEquals(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEquals(response.data['user']['username'], 'admin')
        self.assertEquals(response.data['user']['email'], 'admin@gmail.com')
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEquals(response.data['has_logged_in'], True)

    def test_logout(self):
        # log in a user first
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'password',
        })
        self.assertEquals(response.status_code, 200)
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEquals(response.data['has_logged_in'], True)

        # test logout failure with a wrong http method
        response = self.client.get(LOGOUT_URL)
        self.assertEquals(response.status_code, 405)  # 405: method not allowed

        # test a successful logout
        response = self.client.post(LOGOUT_URL)
        self.assertEquals(response.status_code, 200)
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEquals(response.data['has_logged_in'], False)

    def test_signup(self):
        # test signup with wrong http method
        response = self.client.get(SIGNUP_URL, {
            'username': self.user.username,
            'email': self.user.email,
            'password': self.user.password,
        })
        self.assertEquals(response.status_code, 405)

        # test signup with invalid username
        response = self.client.post(SIGNUP_URL, {
            'username': 'super loooooooooooooooooooooooooooog username',
            'email': self.user.email,
            'password': self.user.password,
        })
        self.assertEquals(response.data['success'], False)
        self.assertEquals(response.status_code, 400)

        # test signup with invalid email address
        response = self.client.post(SIGNUP_URL, {
            'username': self.user.username,
            'email': 'invalid email address',
            'password': self.user.password,
        })
        self.assertEquals(response.data['success'], False)
        self.assertEquals(response.status_code, 400)

        # test signup with short password
        response = self.client.post(SIGNUP_URL, {
            'username': self.user.username,
            'email': self.user.email,
            'password': 123,
        })
        self.assertEquals(response.data['success'], False)
        self.assertEquals(response.status_code, 400)

        # test signup success
        data = {
            'username': 'johndoe',
            'email': 'jd@hotmail.com',
            'password': 'valid_password',
        }
        response = self.client.post(SIGNUP_URL, data)
        self.assertEquals(response.data['success'], True)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data['user']['username'], data['username'])
        self.assertEquals(response.data['user']['email'], data['email'])

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEquals(response.data['has_logged_in'], True)

        # test signup with username already used
        response = self.client.post(SIGNUP_URL, {
            'username': 'johndoe',
            'email': 'jd1@hotmail.com',
            'password': 'valid_password',
        })
        self.assertEquals(response.data['success'], False)
        self.assertEquals(response.data['errors']['username'][0], 'This username has been occupied.')




