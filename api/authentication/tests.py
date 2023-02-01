import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django_redis import get_redis_connection

from datetime import datetime, timedelta
from freezegun import freeze_time

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from authentication.invalid_login import InvalidLoginCache
from authentication.models import (
    EmailVerificationToken, PhoneVerificationToken, TwoFactorAuthToken,)
from authentication.utils import AuthCommands
from custom_db_logger.models import StatusLog
from custom_db_logger.utils import LogLevels
from utils.testing import test_user_1, test_user_2, create_user, log_msg_regex


@override_settings(DJANGO_ENV='test')
class AuthenticationTest(APITestCase):
    databases = '__all__'

    def tearDown(self):
        get_redis_connection('default').flushall()

    # def test_register_fail_missing_info(self):
    #     res_fail = self.client.post(reverse('register'), data={})
    #     self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertListEqual(res_fail.data['name'], ['This field is required.'])
    #     self.assertListEqual(res_fail.data['email'], ['This field is required.'])
    #     self.assertListEqual(res_fail.data['password'], ['This field is required.'])
    #     self.assertListEqual(res_fail.data['password_2'], ['This field is required.'])
    #     log = StatusLog.objects.using('logger').latest('created_at')
    #     self.assertRegex(log.msg, log_msg_regex('Missing register data.', LogLevels.ERROR))
    #     self.assertEqual(log.command, AuthCommands.REGISTER)
    #     self.assertEqual(len(mail.outbox), 1)
    #     self.assertEqual(mail.outbox[0].subject,
    #         f'{settings.EMAIL_SUBJECT_PREFIX}ERROR: Missing register data.')
    #     self.assertListEqual(mail.outbox[0].to, ['contact@simplepasswords.app'])
    #     self.assertEqual(StatusLog.objects.using('logger').count(), 1)

    # def test_register_fail_empty_info(self):
    #     res_fail = self.client.post(reverse('register'), data={
    #         'email': '',
    #         'name': '',
    #         'password': '',
    #         'password_2': '',
    #     })
    #     self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertListEqual(res_fail.data['name'], ['This field may not be blank.'])
    #     self.assertListEqual(res_fail.data['email'], ['This field may not be blank.'])
    #     self.assertListEqual(res_fail.data['password'], ['This field may not be blank.'])
    #     self.assertListEqual(res_fail.data['password_2'], ['This field may not be blank.'])
    #     log = StatusLog.objects.using('logger').latest('created_at')
    #     self.assertRegex(log.msg, log_msg_regex('Missing register data.', LogLevels.ERROR))
    #     self.assertEqual(log.command, AuthCommands.REGISTER)
    #     self.assertEqual(len(mail.outbox), 1)
    #     self.assertEqual(mail.outbox[0].subject,
    #         f'{settings.EMAIL_SUBJECT_PREFIX}ERROR: Missing register data.')
    #     self.assertListEqual(mail.outbox[0].to, ['contact@simplepasswords.app'])
    #     self.assertEqual(StatusLog.objects.using('logger').count(), 1)

    # def test_register_fail_invalid_info(self):
    #     res_fail = self.client.post(reverse('register'), data={
    #         'email': 'bademail.com',
    #         'name': 'Bad name #$',
    #         'password': test_user_1['password'],
    #         'password_2': test_user_1['password'],
    #     })
    #     self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertListEqual(res_fail.data['name'], ['Please enter a valid name.'])
    #     self.assertListEqual(res_fail.data['email'], ['Please enter a valid email address.'])
    #     self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    # def test_register_fail_invalid_password(self):
    #     res_1 = self.client.post(reverse('register'), data={
    #         'email': test_user_1['email'],
    #         'name': test_user_1['name'],
    #         'password': '898980',
    #         'password_2': '898980',
    #     })
    #     self.assertEqual(res_1.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertListEqual(res_1.data['non_field_errors'], [
    #         'This password is too short. It must contain at least 8 characters.',
    #         'This password is entirely numeric.',
    #     ])
    #     res_2 = self.client.post(reverse('register'), data={
    #         'email': test_user_1['email'],
    #         'name': test_user_1['name'],
    #         'password': test_user_1['email'],
    #         'password_2': test_user_1['email'],
    #     })
    #     self.assertEqual(res_2.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertListEqual(res_2.data['non_field_errors'], [
    #         'The password is too similar to the email address.',
    #     ])
    #     res_3 = self.client.post(reverse('register'), data={
    #         'email': test_user_1['email'],
    #         'name': test_user_1['name'],
    #         'password': 'asdfqwer',
    #         'password_2': 'asdfqwer',
    #     })
    #     self.assertEqual(res_3.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertListEqual(res_3.data['non_field_errors'], ['This password is too common.'])
    #     res_4 = self.client.post(reverse('register'), data={
    #         'email': test_user_1['email'],
    #         'name': test_user_1['name'],
    #         'password': test_user_1['password'],
    #         'password_2': 'asdfqwer',
    #     })
    #     self.assertEqual(res_4.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertListEqual(res_4.data['non_field_errors'], ['Passwords do not match.'])
    #     self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    # def test_successful_user_register(self):
    #     response = self.client.post(reverse('register'), data={
    #         'email': test_user_1['email'],
    #         'name': test_user_1['name'],
    #         'password': test_user_1['password'],
    #         'password_2': test_user_1['password'],
    #     })
    #     user = get_user_model().objects.last()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['user']['user_slug'], user.user_slug)
    #     self.assertEqual(response.data['user']['email'], user.email)
    #     self.assertEqual(response.data['user']['name'], user.name)
    #     self.assertFalse(response.data['user']['email_is_verified'])
    #     self.assertFalse(response.data['user']['phone_number_is_verified'])
    #     self.assertEqual(response.data['user']['truncated_phone_number'], '')
    #     self.assertFalse(response.data['user']['tfa_is_enabled'])
    #     self.assertRegex(response.data['token'], r'^[\w-]{64}$')
    #     self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    # def test_resigter_fail_already_exists(self):
    #     user = get_user_model().objects.create_user(**test_user_1)
    #     res_fail = self.client.post(reverse('register'), data={
    #         'email': user.email,
    #         'name': user.name,
    #         'password': user.password,
    #         'password_2': user.password,
    #     })
    #     self.assertEqual(res_fail.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertEqual(res_fail.data['detail'], 'Cannot create account with this email.')
    #     self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_user_register_not_found(self):
        response = self.client.post('/api/auth/register', data={
            'email': test_user_1['email'],
            'name': test_user_1['name'],
            'password': test_user_1['password'],
            'password_2': test_user_1['password'],
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Not found.')
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_login_fail_missing_info(self):
        res_fail = self.client.post(reverse('login'), data={})
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(res_fail.data['email'], ['This field is required.'])
        self.assertListEqual(res_fail.data['password'], ['This field is required.'])
        log = StatusLog.objects.using('logger').latest('created_at')
        self.assertRegex(log.msg, log_msg_regex('Missing login data.', LogLevels.ERROR))
        self.assertEqual(log.command, AuthCommands.LOGIN)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
            f'{settings.EMAIL_SUBJECT_PREFIX}ERROR: Missing login data.')
        self.assertListEqual(mail.outbox[0].to, ['contact@simplepasswords.app'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 1)

    def test_login_fail_empty_info(self):
        res_fail = self.client.post(reverse('login'), data={
            'email': '',
            'password': '',
        })
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(res_fail.data['email'], ['This field may not be blank.'])
        self.assertListEqual(res_fail.data['password'], ['This field may not be blank.'])
        log = StatusLog.objects.using('logger').latest('created_at')
        self.assertRegex(log.msg, log_msg_regex('Missing login data.', LogLevels.ERROR))
        self.assertEqual(log.command, AuthCommands.LOGIN)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
            f'{settings.EMAIL_SUBJECT_PREFIX}ERROR: Missing login data.')
        self.assertListEqual(mail.outbox[0].to, ['contact@simplepasswords.app'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 1)

    def test_login_fail_invalid_info(self):
        res_fail = self.client.post(reverse('login'), data={
            'email': 'bademail.com',
            'password': test_user_1['password'],
        })
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(res_fail.data['email'], ['Please enter a valid email address.'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_successful_log_in_and_out(self):
        user = create_user()
        response = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_1['password'],
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['user_slug'], user.user_slug)
        self.assertEqual(response.data['user']['email'], user.email)
        self.assertEqual(response.data['user']['name'], user.name)
        self.assertTrue(response.data['user']['email_is_verified'])
        self.assertFalse(response.data['user']['phone_number_is_verified'])
        self.assertEqual(response.data['user']['truncated_phone_number'], '')
        self.assertFalse(response.data['user']['tfa_is_enabled'])
        self.assertRegex(response.data['token'], r'^[\w-]{64}$')
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_login_fail_user_not_found(self):
        res_fail = self.client.post(reverse('login'), data={
            'email': test_user_2['email'],
            'password': test_user_2['password'],
        })
        self.assertEqual(res_fail.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res_fail.data['detail'], (
            'Failed to log in with the info provided.'
        ))
        self.assertIsNotNone(InvalidLoginCache.get(test_user_2['email']))
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)

    def test_login_fail_lockout(self):
        user = create_user()

        # Test lock after repeated invalid attempts
        for i in range(1, 15):
            # print('\n')
            # print(i)
            res_fail = self.client.post(reverse('login'), data={
                'email': user.email,
                'password': 'wrongPW#2',
            })
            if i < 5:
                self.assertEqual(res_fail.status_code, status.HTTP_401_UNAUTHORIZED)
                self.assertEqual(res_fail.data['detail'], (
                    'Failed to log in with the info provided.'
                ))
            elif i >= 5 and i < 9:
                self.assertEqual(res_fail.status_code, status.HTTP_401_UNAUTHORIZED)
                self.assertEqual(res_fail.data['detail'], (
                    'Failed to log in with the info provided. '
                    'For security purposes, this account will be temporarily '
                    f'locked after {10 - i} more unsuccessful login attempts.'
                ))
            elif i == 9:
                self.assertEqual(res_fail.status_code, status.HTTP_401_UNAUTHORIZED)
                self.assertEqual(res_fail.data['detail'], (
                    'Failed to log in with the info provided. '
                    'For security purposes, this account will be temporarily '
                    f'locked after 1 more unsuccessful login attempt.'
                ))
            elif i == 10:
                self.assertEqual(res_fail.status_code, status.HTTP_403_FORBIDDEN)
                self.assertEqual(res_fail.data['detail'], (
                    'Failed to log in with the info provided. '
                    'You have been temporarily locked out of this account.'
                ))
            elif i > 10:
                self.assertEqual(res_fail.status_code, status.HTTP_403_FORBIDDEN)
                self.assertEqual(res_fail.data['detail'], (
                    'You have been temporarily locked out of this account.'
                ))

        # Test locked even with correct info
        # print('\n')
        # print(15)
        res_success_locked = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_1['password'],
        })
        self.assertEqual(res_success_locked.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res_success_locked.data['detail'], (
            'You have been temporarily locked out of this account.'
        ))

        # Test throttled request after 15 attempts
        # print('\n')
        # print(16)
        res_throttled = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_1['password'],
        })
        self.assertEqual(res_throttled.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Request was throttled.', res_throttled.data['detail'])
        log = StatusLog.objects.using('logger').latest('created_at')
        # print(StatusLogSerializer(log).data)
        self.assertRegex(log.msg, log_msg_regex('Client was throttled.', LogLevels.ERROR))
        self.assertEqual(log.command, AuthCommands.LOGIN)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
            f'{settings.EMAIL_SUBJECT_PREFIX}ERROR: Client was throttled.')
        self.assertListEqual(mail.outbox[0].to, ['contact@simplepasswords.app'])

        # Test throttled but no redundant log
        # print('\n')
        # print(16.5)
        res_throttled_2 = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_1['password'],
        })
        self.assertEqual(res_throttled_2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Request was throttled.', res_throttled_2.data['detail'])
        self.assertEqual(StatusLog.objects.using('logger').count(), 1)

        # Test no throttle after 1 minute passes
        now = datetime.now()
        freezer = freeze_time(timedelta(minutes=1))
        freezer.start()
        self.assertAlmostEqual(datetime.now().timestamp(), now.timestamp() + 60, 3)
        # print('\n')
        # print(17)
        res_no_throttle_still_locked = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_1['password'],
        })
        self.assertEqual(res_no_throttle_still_locked.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res_no_throttle_still_locked.data['detail'], (
            'You have been temporarily locked out of this account.'
        ))
        freezer.stop()

        # Test unlocked after 5 minutes pass
        now = datetime.now()
        freezer = freeze_time(timedelta(minutes=5))
        freezer.start()
        self.assertAlmostEqual(datetime.now().timestamp(), now.timestamp() + 300, 3)
        # print('\n')
        # print(18)
        res_unlocked = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': 'wrongPW#2',
        })
        self.assertEqual(res_unlocked.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res_unlocked.data['detail'], (
            'Failed to log in with the info provided.'
        ))
        # print('\n')
        # print(19)
        response = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_1['password'],
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['user_slug'], user.user_slug)
        self.assertEqual(response.data['user']['email'], user.email)
        self.assertEqual(response.data['user']['name'], user.name)
        self.assertTrue(response.data['user']['email_is_verified'])
        self.assertFalse(response.data['user']['phone_number_is_verified'])
        self.assertEqual(response.data['user']['truncated_phone_number'], '')
        self.assertFalse(response.data['user']['tfa_is_enabled'])
        self.assertRegex(response.data['token'], r'^[\w-]{64}$')
        freezer.stop()
        self.assertEqual(StatusLog.objects.using('logger').count(), 1)

    def test_email_verification(self):
        user = create_user(test_user_2)
        login_1 = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_2['password'],
        })
        self.assertEqual(login_1.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login_1.data['token']}")
        get_1 = self.client.get(reverse('verify_email'))
        self.assertEqual(get_1.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EmailVerificationToken.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Verify your email address')
        self.assertEqual(mail.outbox[0].to, [user.email])
        print('\n')
        print(mail.outbox[0].body)
        print('\n')
        protocol = 'http'
        if not settings.DEBUG:
            protocol += 's'
        email_substring = f'{protocol}://{settings.DOMAIN}/verify_email?token='
        self.assertIn(email_substring, mail.outbox[0].body)
        email_token_1 = re.search(
            re.escape(email_substring) + r'([\w-]{64})', mail.outbox[0].body,
        ).group(1)
        self.assertIsInstance(email_token_1, str)

        # Already requested verification, no additional email
        get_2 = self.client.get(reverse('verify_email'))
        self.assertEqual(get_2.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EmailVerificationToken.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

        # Test create new token and new email after 10 minutes have passed
        now = datetime.now()
        freezer = freeze_time(timedelta(days=7))
        freezer.start()
        self.assertAlmostEqual(
            datetime.now().timestamp(), now.timestamp() + (60 * 60 * 24 * 7), 3,)
        self.client.credentials(HTTP_AUTHORIZATION='')
        login_2 = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_2['password'],
        })
        self.assertEqual(login_2.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login_2.data['token']}")
        get_3 = self.client.get(reverse('verify_email'))
        self.assertEqual(get_3.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EmailVerificationToken.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, 'Verify your email address')
        self.assertEqual(mail.outbox[1].to, [user.email])
        self.assertIn(email_substring, mail.outbox[1].body)
        email_token_2 = re.search(
            re.escape(email_substring) + r'([\w-]{64})', mail.outbox[1].body,
        ).group(1)
        self.assertIsInstance(email_token_2, str)
        self.assertNotEqual(email_token_1, email_token_2)

        # POST verification token
        self.assertFalse(user.email_is_verified)
        post_1 = self.client.post(reverse('verify_email'), data={
            'token': email_token_2,
        })
        self.assertEqual(post_1.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EmailVerificationToken.objects.count(), 0)
        user.refresh_from_db()
        self.assertTrue(user.email_is_verified)
        freezer.stop()

    def test_phone_verification(self):
        user = create_user(dict(test_user_1, phone_number='+12125556789'))
        login_1 = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_1['password'],
        })
        self.assertEqual(login_1.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login_1.data['token']}")
        get_1 = self.client.get(reverse('verify_phone'))
        self.assertEqual(get_1.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRegex(get_1.data['token_string'], r'^[0-9]{6}$')
        self.assertEqual(PhoneVerificationToken.objects.count(), 1)

        # Already requested verification, no additional sms
        get_2 = self.client.get(reverse('verify_phone'))
        self.assertEqual(get_2.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PhoneVerificationToken.objects.count(), 1)
        self.assertIsNone(get_2.data)

        # Test create new phone token after 10 minutes have passed
        now = datetime.now()
        freezer = freeze_time(timedelta(minutes=10))
        freezer.start()
        self.assertAlmostEqual(datetime.now().timestamp(), now.timestamp() + 600, 3)
        self.client.credentials(HTTP_AUTHORIZATION='')
        login_2 = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_1['password'],
        })
        self.assertEqual(login_2.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login_2.data['token']}")
        get_3 = self.client.get(reverse('verify_phone'))
        self.assertEqual(get_3.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PhoneVerificationToken.objects.count(), 2)
        self.assertRegex(get_3.data['token_string'], r'^[0-9]{6}$')
        self.assertNotEqual(get_1.data['token_string'], get_3.data['token_string'])

        # POST verification token
        self.assertFalse(user.phone_number_is_verified)
        post_1 = self.client.post(reverse('verify_phone'), data={
            'token': get_3.data['token_string'],
        })
        self.assertEqual(post_1.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PhoneVerificationToken.objects.count(), 0)
        user.refresh_from_db()
        self.assertTrue(user.phone_number_is_verified)
        freezer.stop()
    
    def test_log_in_two_factor_authentication(self):
        user = create_user(dict(
            test_user_1, phone_number='+12125556789',
            phone_number_is_verified=True, tfa_is_enabled=True,),)
        login_1 = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_1['password'],
        })
        self.assertEqual(login_1.status_code, status.HTTP_201_CREATED)
        self.assertRegex(login_1.data['tfa_token'], r'^[\w-]{64}$')
        self.assertRegex(login_1.data['security_code'], r'^[0-9]{6}$')
        self.assertEqual(TwoFactorAuthToken.objects.count(), 1)
        self.assertEqual(PhoneVerificationToken.objects.count(), 1)

        # Test no repeat security code within 5 minutes
        login_2 = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_1['password'],
        })
        self.assertEqual(login_2.status_code, status.HTTP_201_CREATED)
        self.assertRegex(login_2.data['tfa_token'], r'^[\w-]{64}$')
        self.assertNotEqual(
            login_1.data['tfa_token'], login_2.data['tfa_token'],)
        self.assertNotIn('security_code', login_2.data)
        self.assertEqual(TwoFactorAuthToken.objects.count(), 2)
        self.assertEqual(PhoneVerificationToken.objects.count(), 1)

        # Test new security code after 5 minutes
        now = datetime.now()
        freezer = freeze_time(timedelta(minutes=5))
        freezer.start()
        self.assertAlmostEqual(
            datetime.now().timestamp(), now.timestamp() + 300, 3,)
        login_3 = self.client.post(reverse('login'), data={
            'email': user.email,
            'password': test_user_1['password'],
        })
        self.assertEqual(login_3.status_code, status.HTTP_201_CREATED)
        self.assertRegex(login_3.data['tfa_token'], r'^[\w-]{64}$')
        self.assertNotEqual(
            login_1.data['security_code'], login_3.data['security_code'],)
        self.assertEqual(TwoFactorAuthToken.objects.count(), 3)
        self.assertEqual(PhoneVerificationToken.objects.count(), 2)

        security_code = login_3.data['security_code']
        tfa_token = login_3.data['tfa_token']

        # Fail w/ invalid security_code
        fail_code = self.client.post(reverse('two_factor_auth'), data={
            'email': user.email,
            'security_code': 'code00',
            'tfa_token': tfa_token,
        })
        self.assertEqual(fail_code.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(
            fail_code.data['non_field_errors'], ['Invalid token.'])

        # Fail w/ invalid tfa_token
        fail_token = self.client.post(reverse('two_factor_auth'), data={
            'email': user.email,
            'security_code': security_code,
            'tfa_token': 'not_a_valid_token',
        })
        self.assertEqual(fail_token.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(
            fail_token.data['non_field_errors'], ['Invalid token.'])

        # Success
        tfa_success = self.client.post(reverse('two_factor_auth'), data={
            'email': user.email,
            'security_code': security_code,
            'tfa_token': tfa_token,
        })
        self.assertEqual(tfa_success.status_code, status.HTTP_200_OK)
        self.assertEqual(tfa_success.data['user']['user_slug'], user.user_slug)
        self.assertEqual(tfa_success.data['user']['email'], user.email)
        self.assertEqual(tfa_success.data['user']['name'], user.name)
        self.assertTrue(tfa_success.data['user']['email_is_verified'])
        self.assertTrue(tfa_success.data['user']['phone_number_is_verified'])
        self.assertEqual(
            tfa_success.data['user']['truncated_phone_number'], '********6789',)
        self.assertTrue(tfa_success.data['user']['tfa_is_enabled'])
        self.assertRegex(tfa_success.data['token'], r'^[\w-]{64}$')
        self.assertEqual(TwoFactorAuthToken.objects.count(), 0)
        self.assertEqual(PhoneVerificationToken.objects.count(), 0)
        self.assertEqual(StatusLog.objects.using('logger').count(), 0)