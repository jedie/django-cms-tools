# coding: utf-8

"""
    $ pytest src/tests/test_admin.py
"""

from __future__ import unicode_literals, print_function

import pytest

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.unittest_base import BaseTestCase


@pytest.mark.django_db
class AdminAnonymousTests(BaseTestCase):

    def test_login(self):
        """
        Anonymous will be redirected to the login page.
        """
        response = self.client.get('/admin/')
        self.assertRedirects(response, expected_url='http://testserver/admin/login/?next=/admin/')


@pytest.mark.django_db
class AdminLoggedinTests(AdminAnonymousTests):
    """
    Some basics test with the django admin
    """
    def setUp(self):
        super(AdminLoggedinTests, self).setUp()
        self.create_testusers()

    def test_staff_admin_index(self):
        self.login(usertype='staff')
        response = self.client.get('/admin/')
        self.assertResponse(response,
            must_contain=(
                'Django administration',
                'staff test user',
                'Site administration',
                'You don\'t have permission to edit anything.'
            ),
            must_not_contain=('error', 'traceback'),
            template_name='admin/index.html',
        )

    def test_superuser_admin_index(self):
        self.login(usertype='superuser')
        response = self.client.get('/admin/')
        self.assertResponse(response,
            must_contain=(
                'Django administration',
                'superuser',
                'Site administration',
                '/admin/auth/group/add/',
                '/admin/auth/user/add/',
            ),
            must_not_contain=('error', 'traceback'),
            template_name='admin/index.html',
        )

