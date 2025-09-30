# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""Tests for the 'how did you hear about us' field"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.authentication.forms.auth_forms import RegisterForm

User = get_user_model()


class HowDidYouHearFieldTest(TestCase):
    """Test the new 'how did you hear about us' field"""

    def setUp(self):
        self.valid_form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_number': '+33612345678',
            'birthday': '1990-01-01',
            'gender': 'M',
            'interface_language': 'en',
            'how_did_you_hear': 'search_engine',  # Required field
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!',
            'terms': True,
        }

    def test_form_with_how_did_you_hear_field(self):
        """Test that form includes how_did_you_hear field"""
        form = RegisterForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_form_saves_how_did_you_hear_field(self):
        """Test that the how_did_you_hear field is saved to the user"""
        form = RegisterForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.how_did_you_hear, 'search_engine')

    def test_form_required_how_did_you_hear_field(self):
        """Test that the how_did_you_hear field is now required"""
        data = self.valid_form_data.copy()
        data.pop('how_did_you_hear')
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('how_did_you_hear', form.errors)

    def test_form_empty_how_did_you_hear_field(self):
        """Test that empty how_did_you_hear field is not valid"""
        data = self.valid_form_data.copy()
        data['how_did_you_hear'] = ''
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('how_did_you_hear', form.errors)

    def test_all_how_did_you_hear_choices(self):
        """Test all available choices for how_did_you_hear field"""
        choices = [
            'search_engine',
            'social_media',
            'friend_referral',
            'online_ad',
            'blog_article',
            'app_store',
            'school_university',
            'work_colleague',
            'other',
        ]

        for choice in choices:
            data = self.valid_form_data.copy()
            data['username'] = f'testuser_{choice}'
            data['email'] = f'test_{choice}@example.com'
            data['how_did_you_hear'] = choice
            form = RegisterForm(data=data)
            self.assertTrue(form.is_valid(), f"Form errors for choice '{choice}': {form.errors}")
            user = form.save()
            self.assertEqual(user.how_did_you_hear, choice)