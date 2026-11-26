import os
from datetime import date
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from School.models import Carousel, Notice, brandInformation, brandLogo


class CarouselViewTests(TestCase):
    def setUp(self):
        self.media_directory = TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.settings_override.enable()

    def tearDown(self):
        self.settings_override.disable()
        self.media_directory.cleanup()

    def test_banner_saves_without_optional_title(self):
        response = self.client.post(reverse('crousel'), {
            'title': '   ',
            'image': SimpleUploadedFile('banner.jpg', b'image-bytes', content_type='image/jpeg'),
            'status': 'Active',
        })

        self.assertRedirects(response, reverse('crousel'))
        carousel = Carousel.objects.get()
        self.assertEqual(carousel.title, '')
        self.assertEqual(carousel.status, 'Active')
        self.assertTrue(os.path.isfile(carousel.image.path))

    def test_missing_banner_image_shows_validation_error(self):
        response = self.client.post(reverse('crousel'), {
            'title': 'Homepage banner',
            'status': 'Active',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please select an image for the banner.')
        self.assertFalse(Carousel.objects.exists())


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

    def test_valid_credentials_open_otp_verification(self):
        response = self.client.post(reverse('login'), {
            'email': 'admin@example.com',
            'password': 'StrongPass123!'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_otp_modal'])
        self.assertEqual(len(response.context['show_otp']), 6)
        self.assertEqual(self.client.session['user_id'], self.user.id)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_missing_credentials_show_an_error(self):
        response = self.client.post(reverse('login'), {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter your email and password.')
        self.assertTrue(response.context['show_login_modal'])

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
        news = Notice.objects.create(
            title='School News',
            description='A school update for families.',
            category='news',
            status=True,
        )

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Exam Notice')
        self.assertContains(response, 'School News')
        self.assertContains(response, reverse('download_notice', args=[notice.id]))
        self.assertEqual(list(response.context['notice_list']), [notice])
        self.assertEqual(list(response.context['news_list']), [news])

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


class ContactEnquiryViewTests(TestCase):
    def setUp(self):
        brandInformation.objects.create(
            brand_name="B.M. DAV Public School",
            about_brand="A school community.",
            email="office@example.com",
            address="School Road",
        )

    @patch("School.views.send_mail", return_value=1)
    def test_valid_enquiry_is_sent_to_the_school_email(self, mocked_send_mail):
        response = self.client.post(reverse("contact"), {
            "name": "Parent Name",
            "email": "parent@example.com",
            "phone": "1234567890",
            "subject": "Admission enquiry",
            "message": "Please share admission details.",
        }, follow=True)

        self.assertRedirects(response, reverse("contact"))
        self.assertContains(response, "Your enquiry has been sent to the school.")
        self.assertEqual(mocked_send_mail.call_args.kwargs["recipient_list"], ["office@example.com"])
        self.assertIn("Parent Name", mocked_send_mail.call_args.kwargs["message"])

    @patch("School.views.send_mail")
    def test_invalid_email_is_rejected_without_sending(self, mocked_send_mail):
        response = self.client.post(reverse("contact"), {
            "name": "Parent Name",
            "email": "not-an-email",
            "subject": "Admission enquiry",
            "message": "Please share admission details.",
        })

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Please enter a valid email address.", status_code=400)
        mocked_send_mail.assert_not_called()


class NoticeManagementViewTests(TestCase):
    def test_add_notice_saves_description_and_category_without_an_image(self):
        response = self.client.post(reverse("add_notice"), {
            "title": "School update",
            "description": "Information for families.",
            "category": "news",
            "status": "on",
        })

        self.assertRedirects(response, reverse("notice_list"))
        notice = Notice.objects.get()
        self.assertEqual(notice.title, "School update")
        self.assertEqual(notice.description, "Information for families.")
        self.assertEqual(notice.category, "news")
        self.assertFalse(notice.image)
        self.assertTrue(notice.status)

    def test_edit_notice_updates_description_and_category(self):
        notice = Notice.objects.create(title="Old title")

        response = self.client.post(reverse("edit_notice", args=[notice.id]), {
            "title": "Updated title",
            "description": "Updated description.",
            "category": "news",
            "status": "on",
        })

        self.assertRedirects(response, reverse("notice_list"))
        notice.refresh_from_db()
        self.assertEqual(notice.title, "Updated title")
        self.assertEqual(notice.description, "Updated description.")
        self.assertEqual(notice.category, "news")
        self.assertTrue(notice.status)
