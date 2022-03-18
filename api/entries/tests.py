from django_redis import get_redis_connection

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from custom_db_logger.models import StatusLog
from entries.models import Entry
from utils.testing import create_user, test_user_1


class EntryTest(APITestCase):
    databases = '__all__'

    def setUp(self):
        self.user_1 = create_user()

    def tearDown(self):
        get_redis_connection('default').flushall()

    def test_create_and_list_entries(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")

        # Fail, invalid password
        response_fail_1 = self.client.post(
            reverse('entry-list'),
            data={
                'title': 'FailEntry@1.0.0',
                'value': 'fail_1.0.0',
                'password': 'badPa$$w0rd',
            },
            format='json',)
        self.assertEqual(response_fail_1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(response_fail_1.data['password'], ['Invalid password.'])

        # Fail, missing info
        response_fail_2 = self.client.post(
            reverse('entry-list'),
            data={ 'password': test_user_1['password'] },
            format='json',)
        self.assertEqual(response_fail_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(response_fail_2.data['title'], ['This field is required.'])
        self.assertListEqual(response_fail_2.data['value'], ['This field is required.'])

        response_create_1 = self.client.post(
            reverse('entry-list'),
            data={
                'title': 'First Entry',
                'value': 'value_1.0.0',
                'password': test_user_1['password'],
            },
            format='json',)
        self.assertEqual(response_create_1.status_code, status.HTTP_201_CREATED)
        self.assertRegex(response_create_1.data['slug'], r'^[\w-]{10}$')
        self.assertEqual(response_create_1.data['title'], 'First Entry')
        self.assertIn('created_at', response_create_1.data)
        self.assertNotIn('value', response_create_1.data)
        self.assertNotIn('password', response_create_1.data)

        response_create_2 = self.client.post(
            reverse('entry-list'),
            data={
                'title': 'Second Entry',
                'value': 'value_2.0.0',
                'password': test_user_1['password'],
            },
            format='json',)
        self.assertEqual(response_create_2.status_code, status.HTTP_201_CREATED)
        self.assertRegex(response_create_2.data['slug'], r'^[\w-]{10}$')
        self.assertEqual(response_create_2.data['title'], 'Second Entry')
        self.assertIn('created_at', response_create_2.data)
        self.assertNotIn('value', response_create_2.data)
        self.assertNotIn('password', response_create_2.data)

        response_list_1 = self.client.get(reverse('entry-list'), format='json')
        self.assertEqual(response_list_1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_list_1.data), 2)
        self.assertEqual(response_list_1.data[0]['slug'], response_create_2.data['slug'])
        self.assertEqual(response_list_1.data[1]['slug'], response_create_1.data['slug'])
        self.assertEqual(response_list_1.data[0]['title'], response_create_2.data['title'])
        self.assertEqual(response_list_1.data[1]['title'], response_create_1.data['title'])
        self.assertEqual(response_list_1.data[0]['created_at'], response_create_2.data['created_at'])
        self.assertEqual(response_list_1.data[1]['created_at'], response_create_1.data['created_at'])
        self.assertNotIn('value', response_list_1.data[0])
        self.assertNotIn('password', response_list_1.data[0])
        self.assertNotIn('value', response_list_1.data[1])
        self.assertNotIn('password', response_list_1.data[1])

        # Filter by ?search=s
        response_list_2 = self.client.get('/api/entries/?search=s', format='json')
        self.assertEqual(len(response_list_2.data), 2)
        self.assertEqual(response_list_2.status_code, status.HTTP_200_OK)
        self.assertEqual(response_list_2.data[0]['slug'], response_create_2.data['slug'])
        self.assertEqual(response_list_2.data[1]['slug'], response_create_1.data['slug'])
        self.assertEqual(response_list_2.data[0]['title'], response_create_2.data['title'])
        self.assertEqual(response_list_2.data[1]['title'], response_create_1.data['title'])
        self.assertEqual(response_list_2.data[0]['created_at'], response_create_2.data['created_at'])
        self.assertEqual(response_list_2.data[1]['created_at'], response_create_1.data['created_at'])

        # Filter by ?search=se
        response_list_3 = self.client.get('/api/entries/?search=se', format='json')
        self.assertEqual(len(response_list_3.data), 1)
        self.assertEqual(response_list_3.status_code, status.HTTP_200_OK)
        self.assertEqual(response_list_3.data[0]['slug'], response_create_2.data['slug'])
        self.assertEqual(response_list_3.data[0]['title'], response_create_2.data['title'])
        self.assertEqual(response_list_3.data[0]['created_at'], response_create_2.data['created_at'])

        # Filter by ?search=f
        response_list_4 = self.client.get('/api/entries/?search=f', format='json')
        self.assertEqual(len(response_list_4.data), 1)
        self.assertEqual(response_list_4.status_code, status.HTTP_200_OK)
        self.assertEqual(response_list_4.data[0]['slug'], response_create_1.data['slug'])
        self.assertEqual(response_list_4.data[0]['title'], response_create_1.data['title'])
        self.assertEqual(response_list_4.data[0]['created_at'], response_create_1.data['created_at'])

        # Filter by ?search=
        response_list_5 = self.client.get('/api/entries/?search=', format='json')
        self.assertEqual(len(response_list_5.data), 2)
        self.assertEqual(response_list_5.status_code, status.HTTP_200_OK)
        self.assertEqual(response_list_5.data[0]['slug'], response_create_2.data['slug'])
        self.assertEqual(response_list_5.data[1]['slug'], response_create_1.data['slug'])
        self.assertEqual(response_list_5.data[0]['title'], response_create_2.data['title'])
        self.assertEqual(response_list_5.data[1]['title'], response_create_1.data['title'])
        self.assertEqual(response_list_5.data[0]['created_at'], response_create_2.data['created_at'])
        self.assertEqual(response_list_5.data[1]['created_at'], response_create_1.data['created_at'])

        # Filter by ?search=third
        response_list_6 = self.client.get('/api/entries/?search=third', format='json')
        self.assertListEqual(response_list_6.data, [])
        self.assertEqual(response_list_6.status_code, status.HTTP_200_OK)
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_retrieve_entry(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")

        response_create = self.client.post(
            reverse('entry-list'),
            data={
                'title': 'NewEntry@1.0.0',
                'value': 'value_1.0.0',
                'password': test_user_1['password'],
            },
            format='json',)
        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED)
        self.assertRegex(response_create.data['slug'], r'^[\w-]{10}$')
        self.assertEqual(response_create.data['title'], 'NewEntry@1.0.0')
        self.assertIn('created_at', response_create.data)
        self.assertNotIn('value', response_create.data)
        self.assertNotIn('password', response_create.data)
        slug = response_create.data['slug']

        # Fail, entry not found
        response_fail_1 = self.client.post(
            reverse('entry-retrieve', args=['slugwrong1']),
            data=dict(password=test_user_1['password']),
            format='json',)
        self.assertEqual(response_fail_1.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_fail_1.data['detail'], 'Not found.')

        # Fail, invalid password
        response_fail_2 = self.client.post(
            reverse('entry-retrieve', args=[slug]),
            data=dict(password='badPa$$w0rd'),
            format='json',)
        self.assertEqual(response_fail_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(response_fail_2.data['password'], ['Invalid password.'])

        # Fail, invalid slug
        response_fail_3 = self.client.post(
            '/api/entry_retrieve/invalid/',
            data=dict(password=test_user_1['password']), format='json',)
        self.assertEqual(response_fail_3.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_fail_3.data['detail'], 'Not found.')

        # Success
        response_retrieve = self.client.post(
            reverse('entry-retrieve', args=[slug]),
            data=dict(password=test_user_1['password']),
            format='json',)
        self.assertEqual(response_retrieve.status_code, status.HTTP_200_OK)
        self.assertEqual(response_retrieve.data['slug'], slug)
        self.assertEqual(response_retrieve.data['title'], response_create.data['title'])
        self.assertEqual(response_retrieve.data['created_at'], response_create.data['created_at'])
        self.assertEqual(response_retrieve.data['value'], 'value_1.0.0')
        self.assertNotIn('password', response_retrieve.data)
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_update_entry(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")

        response_create = self.client.post(
            reverse('entry-list'),
            data={
                'title': 'NewEntry@1.0.0',
                'value': 'value_1.0.0',
                'password': test_user_1['password'],
            },
            format='json',)
        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED)
        self.assertRegex(response_create.data['slug'], r'^[\w-]{10}$')
        self.assertEqual(response_create.data['title'], 'NewEntry@1.0.0')
        self.assertIn('created_at', response_create.data)
        self.assertNotIn('value', response_create.data)
        self.assertNotIn('password', response_create.data)

        slug = response_create.data['slug']

        response_update = self.client.put(
            reverse('entry-update', args=[slug]),
            data={
                'title': 'NewEntry@1.0.1',
                'value': 'value_1.0.1',
                'password': test_user_1['password'],
            },
            format='json',)
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        self.assertEqual(response_update.data['slug'], slug)
        self.assertEqual(response_update.data['created_at'], response_create.data['created_at'])
        self.assertEqual(response_update.data['title'], 'NewEntry@1.0.1')
        self.assertEqual(response_update.data['value'], 'value_1.0.1')
        self.assertNotIn('password', response_update.data)
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)
    
    def test_successful_destroy_entry(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")

        response_create = self.client.post(
            reverse('entry-list'),
            data={
                'title': 'NewEntry@1.0.0',
                'value': 'value_1.0.0',
                'password': test_user_1['password'],
            },
            format='json',)
        self.assertEqual(response_create.status_code, status.HTTP_201_CREATED)
        self.assertRegex(response_create.data['slug'], r'^[\w-]{10}$')
        self.assertEqual(response_create.data['title'], 'NewEntry@1.0.0')
        self.assertIn('created_at', response_create.data)
        self.assertNotIn('value', response_create.data)
        self.assertNotIn('password', response_create.data)
        self.assertEqual(Entry.objects.using('default').count(), 1)

        slug = response_create.data['slug']

        response_retrieve = self.client.post(
            reverse('entry-destroy', args=[slug]),
            data=dict(password=test_user_1['password']),
            format='json',)
        self.assertEqual(response_retrieve.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Entry.objects.using('default').count(), 0)
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)