import re

from cryptocode import encrypt
from django.contrib.auth import get_user_model
from django.db import connections

from entries.models import Entry
from custom_db_logger.utils import LogLevels


test_user_1 = {
    'name': 'Jane Doe',
    'email': 'janedoe@email.com',
    'password': 'pAssw0rd!',
    'email_is_verified': True,
}

test_user_2 = {
    'name': 'John Doe',
    'email': 'johndoe@email.com',
    'password': 'pAssw0rd!',
}

test_user_3 = {
    'name': 'Jesse Doe',
    'email': 'jessedoe@email.com',
    'password': 'pAssw0rd!',
}

test_user_4 = {
    'name': 'Jean Doe',
    'email': 'jeandoe@email.com',
    'password': 'pAssw0rd!',
}

test_superuser = {
    'name': 'Super User',
    'email': 'superuser@email.com',
    'password': 'Admin!123',
}

test_entry_1 = {
    'title': 'TestEntry@1.0.0',
    'value': 'test_value_1.0.0',
}

test_entry_2 = {
    'title': 'TestEntry@2.0.0',
    'value': 'test_value_2.0.0',
}


def create_user(data=test_user_1):
    return get_user_model().objects.create_user(**data)


def create_entries(user, password, entry_1=test_entry_1, entry_2=test_entry_2):
    entry_1 = dict(entry_1, value=encrypt(entry_1['value'], password))
    entry_2 = dict(entry_2, value=encrypt(entry_2['value'], password))
    e1 = Entry.objects.create(user=user, **entry_1)
    e2 = Entry.objects.create(user=user, **entry_2)
    return Entry.objects.filter(slug__in=[e1.slug, e2.slug])


def create_superuser(data=test_superuser):
    return get_user_model().objects.create_superuser(**data)


def force_drop_test_databases():
    test_dbs = [
        {
            'db_alias': 'default',
            'db_name': 'test_simplepasswords_default_db',
        },
        {
            'db_alias': 'logger',
            'db_name': 'test_simplepasswords_logger_db',
        },
    ]

    for test_db in test_dbs:
        db_alias = test_db['db_alias']
        with connections[db_alias].cursor() as cursor:
            db_name = test_db['db_name']
            cursor.execute(
                f'ALTER DATABASE {db_name} CONNECTION LIMIT 0')
            cursor.execute("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s;
            """, [db_name,])
            cursor.execute(f'DROP DATABASE {db_name}')


def log_msg_regex(msg, log_level=None):
    if log_level:
        level_regex = re.escape(LogLevels(log_level).name)
    else:
        level_regex = r'(NOTSET|DEBUG|INFO|WARNING|ERROR|CRITICAL)'
    return (
        r'^' + level_regex +
        r' [\d]{4}-[\d]{2}-[\d]{2} [\d]{2}:[\d]{2}:[\d]{2},[\d]{3} .* line [\d]{0,6} in [\w-]*: ' +
        re.escape(msg) + r'$')