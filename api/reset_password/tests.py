import re

from django.conf import settings
from django.core import mail
from django.core.cache import cache
from django.test import override_settings

from datetime import datetime, timedelta
from freezegun import freeze_time

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from reset_password.models import (
    ResetPasswordEmailToken, ResetPasswordPhoneToken,
    ResetPasswordSubmitToken,)
from utils.testing import test_user_1, test_user_2, create_user


@override_settings(DJANGO_ENV='test')
class AuthenticationTest(APITestCase):
    databases = '__all__'

    def tearDown(self):
        cache.clear()

    def test_reset_password_request(self):
        # Successful request w/ existing user
        user = create_user()
        response_1 = self.client.post(reverse('reset_password_request'), data={
            'email': user.email,
        })
        self.assertEqual(response_1.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        subject = 'Reset password for SimplePasswords account'
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].to, [user.email])
        print('\n')
        print(mail.outbox[0].body)
        print('\n')
        protocol = 'http'
        if not settings.DEBUG:
            protocol += 's'
        email_substring = f'{protocol}://{settings.DOMAIN}/reset_password/email?token='
        self.assertIn(email_substring, mail.outbox[0].body)
        rpw_email_token_1 = re.search(
            re.escape(email_substring) + r'([\w-]{64})',
            mail.outbox[0].body,
        ).group(1)
        self.assertIsInstance(rpw_email_token_1, str)

        # Already requested w/ existing user, no additional email
        response_2 = self.client.post(reverse('reset_password_request'), data={
            'email': user.email,
        })
        self.assertEqual(response_2.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

        # Non-existing user, successful request but no email
        response_3 = self.client.post(reverse('reset_password_request'), data={
            'email': 'notauser@email.com',
        })
        self.assertEqual(response_3.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

        # Test create new token and new email after 1 hour has passed
        now = datetime.now()
        freezer = freeze_time(timedelta(hours=1))
        freezer.start()
        self.assertAlmostEqual(
            datetime.now().timestamp(), now.timestamp() + 3600, 3)
        response_4 = self.client.post(reverse('reset_password_request'), data={
            'email': user.email,
        })
        self.assertEqual(response_4.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, subject)
        self.assertEqual(mail.outbox[1].to, [user.email])
        self.assertIn(email_substring, mail.outbox[1].body)
        rpw_email_token_2 = re.search(
            re.escape(email_substring) + r'([\w-]{64})',
            mail.outbox[1].body,
        ).group(1)
        self.assertIsInstance(rpw_email_token_2, str)
        self.assertNotEqual(rpw_email_token_1, rpw_email_token_2)
        freezer.stop()

    def test_reset_password_email(self):
        user = create_user(dict(
            test_user_1, phone_number='+12125556789',
            phone_number_is_verified=True,),)

        # Fail after 1 hour has passed
        rpw_email_token_expire = ResetPasswordEmailToken.objects.create(
            email=user.email, expiry=timedelta(hours=1),)
        now = datetime.now()
        freezer = freeze_time(timedelta(hours=1))
        freezer.start()
        self.assertAlmostEqual(
            datetime.now().timestamp(), now.timestamp() + 3600, 3)
        fail_expire = self.client.post(reverse('reset_password_email'), data={
            'email': user.email,
            'email_token': rpw_email_token_expire[1],
        })
        self.assertEqual(fail_expire.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(
            fail_expire.data['non_field_errors'], ['Invalid token.'])
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 0)
        self.assertEqual(ResetPasswordPhoneToken.objects.count(), 0)

        rpw_email_token = ResetPasswordEmailToken.objects.create(
            email=user.email, expiry=timedelta(hours=1),)

        # Fail w/ invalid token
        fail_token = self.client.post(reverse('reset_password_email'), data={
            'email': user.email,
            'email_token': 'this_is_not_a_matching_token',
        })
        self.assertEqual(fail_token.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(
            fail_token.data['non_field_errors'], ['Invalid token.'])
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 1)
        self.assertEqual(ResetPasswordPhoneToken.objects.count(), 0)

        # Fail w/ non-matching email
        fail_email = self.client.post(reverse('reset_password_email'), data={
            'email': test_user_2['email'],
            'email_token': rpw_email_token[1],
        })
        self.assertEqual(fail_email.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(
            fail_email.data['non_field_errors'], ['Invalid token.'])
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 1)
        self.assertEqual(ResetPasswordPhoneToken.objects.count(), 0)

        # Successfully send sms
        response_1 = self.client.post(reverse('reset_password_email'), data={
            'email': user.email,
            'email_token': rpw_email_token[1],
        })
        self.assertEqual(response_1.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRegex(response_1.data['token_string'], r'^[0-9]{6}$')
        self.assertEqual(ResetPasswordPhoneToken.objects.count(), 1)

        # Already requested verification, no additional sms
        response_2 = self.client.post(reverse('reset_password_email'), data={
            'email': user.email,
            'email_token': rpw_email_token[1],
        })
        self.assertEqual(response_2.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(response_2.data)
        self.assertEqual(ResetPasswordPhoneToken.objects.count(), 1)

    def test_reset_password_phone(self):
        user = create_user(dict(
            test_user_1, phone_number='+12125556789',
            phone_number_is_verified=True,),)

        rpw_email_token = ResetPasswordEmailToken.objects.create(
            email=user.email, expiry=timedelta(hours=1),)
        
        rpw_phone_token_expire = ResetPasswordPhoneToken.objects.create(
            email=user.email, expiry=timedelta(minutes=10),)
        
        # Fail after 10 minutes have passed
        now = datetime.now()
        freezer = freeze_time(timedelta(minutes=10))
        freezer.start()
        self.assertAlmostEqual(
            datetime.now().timestamp(), now.timestamp() + 600, 3)
        
        fail_expire = self.client.post(reverse('reset_password_phone'), data={
            'email': user.email,
            'email_token': rpw_email_token[1],
            'phone_token': rpw_phone_token_expire[1],
        })
        self.assertEqual(fail_expire.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(
            fail_expire.data['non_field_errors'], ['Invalid token.'])
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 1)
        self.assertEqual(ResetPasswordPhoneToken.objects.count(), 0)
        self.assertEqual(ResetPasswordSubmitToken.objects.count(), 0)

        rpw_phone_token = ResetPasswordPhoneToken.objects.create(
            email=user.email, expiry=timedelta(minutes=10),)

        # Fail w/ invalid email token
        fail_email_token = self.client.post(reverse('reset_password_phone'), data={
            'email': user.email,
            'email_token': 'this_is_not_a_matching_token',
            'phone_token': rpw_phone_token[1],
        })
        self.assertEqual(fail_email_token.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(
            fail_email_token.data['non_field_errors'], ['Invalid token.'])
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 1)
        self.assertEqual(ResetPasswordPhoneToken.objects.count(), 1)
        self.assertEqual(ResetPasswordSubmitToken.objects.count(), 0)

        # Fail w/ invalid phone token
        fail_phone_token = self.client.post(reverse('reset_password_phone'), data={
            'email': user.email,
            'email_token': rpw_email_token[1],
            'phone_token': 'this_is_not_a_matching_token',
        })
        self.assertEqual(fail_phone_token.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(
            fail_phone_token.data['non_field_errors'], ['Invalid token.'])
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 1)
        self.assertEqual(ResetPasswordPhoneToken.objects.count(), 1)
        self.assertEqual(ResetPasswordSubmitToken.objects.count(), 0)

        # Fail w/ non-matching email
        fail_email = self.client.post(reverse('reset_password_phone'), data={
            'email': test_user_2['email'],
            'email_token': rpw_email_token[1],
            'phone_token': rpw_phone_token[1],
        })
        self.assertEqual(fail_email.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(
            fail_email.data['non_field_errors'], ['Invalid token.'])
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 1)
        self.assertEqual(ResetPasswordPhoneToken.objects.count(), 1)
        self.assertEqual(ResetPasswordSubmitToken.objects.count(), 0)

        # Success
        response_1 = self.client.post(reverse('reset_password_phone'), data={
            'email': user.email,
            'email_token': rpw_email_token[1],
            'phone_token': rpw_phone_token[1],
        })
        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        self.assertRegex(response_1.data['token'], r'^[\w-]{64}$')
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 1)
        self.assertEqual(ResetPasswordPhoneToken.objects.count(), 1)
        self.assertEqual(ResetPasswordSubmitToken.objects.count(), 1)

        # Already requested verification, no additional submit_token
        response_2 = self.client.post(reverse('reset_password_phone'), data={
            'email': user.email,
            'email_token': rpw_email_token[1],
            'phone_token': rpw_phone_token[1],
        })
        self.assertEqual(response_2.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(response_2.data)
        self.assertEqual(ResetPasswordEmailToken.objects.count(), 1)
        self.assertEqual(ResetPasswordPhoneToken.objects.count(), 1)
        self.assertEqual(ResetPasswordSubmitToken.objects.count(), 1)