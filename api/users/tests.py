from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django_redis import get_redis_connection

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from custom_db_logger.models import StatusLog
from custom_db_logger.utils import LogLevels
from users.utils import UserCommands
from utils.testing import (
    test_user_1, test_user_2, test_entry_1, test_entry_2,
    create_user, create_entries, log_msg_regex,)


class UserAccountTest(APITestCase):
    databases = '__all__'

    def setUp(self):
        self.user_1 = create_user(dict(
            test_user_1, phone_number='+12125556789',
            phone_number_is_verified=True,),)
        self.user_2 = create_user(test_user_2)
        self.entries = create_entries(self.user_1, test_user_1['password'])

    def tearDown(self):
        get_redis_connection('default').flushall()

    def test_user_update_fail_missing_password(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        user_slug = login.data['user']['user_slug']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        url = f'/api/users/{user_slug}/'
        patch = self.client.patch(url, data={ 'name': 'New' }, format='json')
        self.assertEqual(patch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(patch.data['detail'], 'Error updating account.')
        log = StatusLog.objects.using('logger').latest('created_at')
        self.assertRegex(log.msg, log_msg_regex('Error updating user.', LogLevels.ERROR))
        self.assertEqual(log.command, UserCommands.UPDATE)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
            f'{settings.EMAIL_SUBJECT_PREFIX}ERROR: Error updating user.')
        self.assertListEqual(mail.outbox[0].to, ['contact@simplepasswords.app'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 1)

    def test_user_update_fail_wrong_password(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        user_slug = login.data['user']['user_slug']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        url = f'/api/users/{user_slug}/'
        patch = self.client.patch(
            url,
            data={ 'name': 'New', 'current_password': 'wrongPw#1' },
            format='json',
        )
        self.assertEqual(patch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(patch.data['current_password'], ['Invalid password.'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_user_update_email_fail_already_in_use(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        user_slug = login.data['user']['user_slug']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        url = f'/api/users/{user_slug}/'
        patch = self.client.patch(
            url,
            data={
                'email': self.user_2.email,
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(patch.data['email'], [
            'Email address unavailable - please choose a different one.',
        ])
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)        

    def test_user_update_password_fail_invalid(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        user_slug = login.data['user']['user_slug']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        url = f'/api/users/{user_slug}/'

        # All numeric
        patch_1 = self.client.patch(
            url,
            data={
                'password': '89898022',
                'password_2': '89898022',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch_1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(patch_1.data['password'], [
            'This password is entirely numeric.',
        ])

        # Similar to email
        patch_2 = self.client.patch(
            url,
            data={
                'password': test_user_1['email'],
                'password_2': test_user_1['email'],
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(patch_2.data['password'], [
            'The password is too similar to the email address.',
        ])

        # Too common
        patch_3 = self.client.patch(
            url,
            data={
                'password': 'asdfqwer',
                'password_2': 'asdfqwer',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch_3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(patch_3.data['password'], ['This password is too common.'])

        # Too short, add log
        patch_4 = self.client.patch(
            url,
            data={
                'password': 'pAssW0#',
                'password_2': 'pAssW0#',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch_4.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(patch_4.data['password'], [
            'This password is too short. It must contain at least 8 characters.',
        ])
        log_1 = StatusLog.objects.using('logger').latest('created_at')
        self.assertRegex(log_1.msg, log_msg_regex('Short password.', LogLevels.ERROR))
        self.assertEqual(log_1.command, UserCommands.UPDATE)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
            f'{settings.EMAIL_SUBJECT_PREFIX}ERROR: Short password.')
        self.assertListEqual(mail.outbox[0].to, ['contact@simplepasswords.app'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 1)

        # Not matching, add log
        patch_5 = self.client.patch(
            url,
            data={
                'password': 'newPassw0rd$',
                'password_2': 'newPassw0rd',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch_5.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(patch_5.data['password_2'], ['Passwords do not match.'])
        log_2 = StatusLog.objects.using('logger').latest('created_at')
        self.assertRegex(log_2.msg, log_msg_regex('Error changing user password.', LogLevels.ERROR))
        self.assertEqual(log_2.command, UserCommands.UPDATE)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject,
            f'{settings.EMAIL_SUBJECT_PREFIX}ERROR: Error changing user password.')
        self.assertListEqual(mail.outbox[1].to, ['contact@simplepasswords.app'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 2)

        # Missing password, add log
        patch_6 = self.client.patch(
            url,
            data={
                'password_2': 'newPassw0rd$',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch_6.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(patch_6.data['password'], ['Invalid password change.'])
        log_3 = StatusLog.objects.using('logger').latest('created_at')
        self.assertRegex(log_3.msg, log_msg_regex('Error changing user password.', LogLevels.ERROR))
        self.assertEqual(log_3.command, UserCommands.UPDATE)
        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[2].subject,
            f'{settings.EMAIL_SUBJECT_PREFIX}ERROR: Error changing user password.')
        self.assertListEqual(mail.outbox[2].to, ['contact@simplepasswords.app'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 3)

    def test_user_update_password_fail_same_as_slug(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        user_slug = login.data['user']['user_slug']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        url = f'/api/users/{user_slug}/'
        patch = self.client.patch(
            url,
            data={
                'password': user_slug,
                'password_2': user_slug,
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(patch.data['password'], ['Password cannot be your user ID.'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_successful_user_password_update(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        user_slug = login.data['user']['user_slug']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        url = f'/api/users/{user_slug}/'
        patch = self.client.patch(
            url,
            data={
                'password': 'newPassw0rd$',
                'password_2': 'newPassw0rd$',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)

        # Test new password
        login_1 = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': 'newPassw0rd$',
        })
        self.assertEqual(login_1.status_code, status.HTTP_200_OK)

        # Test old password fail
        login_2 = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        self.assertEqual(login_2.status_code, status.HTTP_401_UNAUTHORIZED)

        # Check entries are re-encrypted with new password
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login_1.data['token']}")
        retrieve_1 = self.client.post(
            reverse('entry-retrieve', args=[self.entries[0].slug]),
            data=dict(password='newPassw0rd$'),
            format='json',)
        self.assertEqual(retrieve_1.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_1.data['value'], test_entry_2['value'])

        retrieve_2 = self.client.post(
            reverse('entry-retrieve', args=[self.entries[1].slug]),
            data=dict(password='newPassw0rd$'),
            format='json',)
        self.assertEqual(retrieve_2.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_2.data['value'], test_entry_1['value'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_cannot_access_another_users_info(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        url = f'/api/users/{self.user_2.user_slug}/'
        res_fail = self.client.patch(
            url,
            data={
                'email': 'newemail.willfail@email.com',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(res_fail.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res_fail.data['detail'], 'User denied access.')
        log = StatusLog.objects.using('logger').latest('created_at')
        self.assertRegex(log.msg, log_msg_regex('User denied access.', LogLevels.ERROR))
        self.assertEqual(log.command, UserCommands.UPDATE)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
            f'{settings.EMAIL_SUBJECT_PREFIX}ERROR: User denied access.')
        self.assertListEqual(mail.outbox[0].to, ['contact@simplepasswords.app'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 1)

    def test_user_update_fail_empty_info(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        user_slug = login.data['user']['user_slug']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        url = f'/api/users/{user_slug}/'
        patch = self.client.patch(
            url,
            data={
                'name': '',
                'email': '',
                'phone_number': '',
                'password': '',
                'password_2': '',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(patch.data['name'], ['This field may not be blank.'])
        self.assertListEqual(patch.data['email'], ['This field may not be blank.'])
        log = StatusLog.objects.using('logger').latest('created_at')
        self.assertRegex(log.msg, log_msg_regex('Blank user update.', LogLevels.ERROR))
        self.assertEqual(log.command, UserCommands.UPDATE)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
            f'{settings.EMAIL_SUBJECT_PREFIX}ERROR: Blank user update.')
        self.assertListEqual(mail.outbox[0].to, ['contact@simplepasswords.app'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 1)

    def test_user_update_fail_invalid_info(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        user_slug = login.data['user']['user_slug']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        url = f'/api/users/{user_slug}/'
        patch = self.client.patch(
            url,
            data={
                'name': 'Bad name #$',
                'email': 'bademail.com',
                'phone_number': '+133',
                'password': '',
                'password_2': '',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(patch.data['name'], ['Please enter a valid name.'])
        self.assertListEqual(patch.data['email'], ['Please enter a valid email address.'])
        self.assertListEqual(patch.data['phone_number'], ['Enter a valid phone number.'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_successful_user_info_update(self):
        self.assertTrue(self.user_1.email_is_verified)
        self.assertTrue(self.user_1.phone_number_is_verified)
        login = self.client.post(reverse('login'), data={
            'email': self.user_1.email,
            'password': test_user_1['password'],
        })
        user_slug = login.data['user']['user_slug']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        url = f'/api/users/{user_slug}/'

        # Successful update
        patch_1 = self.client.patch(
            url,
            data={
                'name': 'New Name',
                'email': 'fake3@email.com',
                'phone_number': '+12125551234',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch_1.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_1.data['name'], 'New Name')
        self.assertEqual(patch_1.data['email'], 'fake3@email.com')
        self.assertFalse(patch_1.data['email_is_verified'])
        self.assertFalse(patch_1.data['phone_number_is_verified'])
        self.assertEqual(patch_1.data['truncated_phone_number'], '********1234')

        # Test remove phone_number via ''
        patch_2 = self.client.patch(
            url,
            data={
                'phone_number': '',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch_2.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_2.data['name'], 'New Name')
        self.assertEqual(patch_2.data['email'], 'fake3@email.com')
        self.assertFalse(patch_2.data['email_is_verified'])
        self.assertFalse(patch_1.data['phone_number_is_verified'])
        self.assertEqual(patch_2.data['truncated_phone_number'], '')

        # Update again
        patch_3 = self.client.patch(
            url,
            data={
                'phone_number': '+12125551234',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch_3.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_3.data['name'], 'New Name')
        self.assertEqual(patch_3.data['email'], 'fake3@email.com')
        self.assertFalse(patch_3.data['email_is_verified'])
        self.assertFalse(patch_1.data['phone_number_is_verified'])
        self.assertEqual(patch_3.data['truncated_phone_number'], '********1234')

        # Test remove phone_number via None
        patch_4 = self.client.patch(
            url,
            data={
                'phone_number': None,
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch_4.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_4.data['name'], 'New Name')
        self.assertEqual(patch_4.data['email'], 'fake3@email.com')
        self.assertFalse(patch_4.data['email_is_verified'])
        self.assertFalse(patch_1.data['phone_number_is_verified'])
        self.assertEqual(patch_4.data['truncated_phone_number'], '')
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_user_can_deactivate_account(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        user_slug = login.data['user']['user_slug']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        url = f'/api/users/{user_slug}/'
        delete_fail = self.client.delete(
            url,
            data={
                'current_password': 'wrong',
                'email': test_user_1['email'] + 'salt',
            },
            format='json',
        )
        self.assertEqual(delete_fail.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(delete_fail.data['current_password'], ['Invalid password.'])
        self.assertListEqual(delete_fail.data['email'], ['Invalid email.'])
        delete = self.client.delete(
            url,
            data={
                'current_password': test_user_1['password'],
                'email': test_user_1['email'],
            },
            format='json',
        )
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        user = get_user_model().objects.get(user_slug=user_slug)
        self.assertFalse(user.is_active)
        patch_fail = self.client.patch(
            url,
            data={
                'name': 'New Name',
                'current_password': test_user_1['password'],
            },
            format='json',
        )
        self.assertEqual(patch_fail.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(patch_fail.data['detail'], 'Invalid token.')
        self.client.credentials()
        login_fail = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        self.assertEqual(login_fail.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(login_fail.data['detail'], (
            'Failed to log in with the info provided.'
        ))
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_successful_retrieve_user(self):
        login = self.client.post(reverse('login'), data={
            'email': test_user_1['email'],
            'password': test_user_1['password'],
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        get = self.client.get(reverse('users'))
        self.assertEqual(get.status_code, status.HTTP_200_OK)
        self.assertEqual(get.data['name'], test_user_1['name'])
        self.assertEqual(get.data['email'], test_user_1['email'])
        self.assertTrue(get.data['email_is_verified'])
        self.assertTrue(get.data['phone_number_is_verified'])
        self.assertEqual(get.data['truncated_phone_number'], '********6789')
        self.assertEqual(get.headers['Access-Control-Expose-Headers'], 'X-Client-Ip')
        self.assertEqual(get.headers['X-Client-Ip'], '127.0.0.1')
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)