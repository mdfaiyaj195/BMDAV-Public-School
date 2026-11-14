import os
from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from School.models import Notice, brandLogo


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='StrongPass123!'
        )

    def test_invalid_credentials_do_not_redirect_to_dashboard(self):
        response = self.client.post(reverse('login'), {
            'email': 'admin@example.com',
            'password': 'wrong-password'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid Email or Password')
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_valid_credentials_redirect_to_dashboard(self):
        response = self.client.post(reverse('login'), {
            'email': 'admin@example.com',
            'password': 'StrongPass123!'
        }, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_brand_logo_post_redirects_and_prevents_duplicate_save_on_refresh(self):
        response = self.client.post(reverse('brand-logo'), {
            'logo': SimpleUploadedFile('logo.png', b'fake-image-bytes', content_type='image/png'),
            'favicon': SimpleUploadedFile('favicon.png', b'fake-favicon-bytes', content_type='image/png')
        }, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('brand-logo'))
        self.assertEqual(brandLogo.objects.count(), 1)

    def test_homepage_shows_active_notices_and_download_link(self):
        notice = Notice.objects.create(
            title='Exam Notice',
            image=SimpleUploadedFile('exam.pdf', b'pdf-bytes', content_type='application/pdf'),
            publish_date=date.today(),
            status=True,
        )

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Exam Notice')
        self.assertContains(response, reverse('download_notice', args=[notice.id]))

    def test_notice_download_returns_file(self):
        notice = Notice.objects.create(
            title='Download Notice',
            image=SimpleUploadedFile('notice.pdf', b'pdf-content', content_type='application/pdf'),
            publish_date=date.today(),
            status=True,
        )

        response = self.client.get(reverse('download_notice', args=[notice.id]))

        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment; filename="notice.pdf"', response['Content-Disposition'])
        self.assertEqual(response.content, b'pdf-content')
