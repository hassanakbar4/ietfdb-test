from django.urls import reverse

import debug                            # pyflakes:ignore

from ietf.utils.test_utils import TestCase
from ietf.person.factories import PersonFactory, UserFactory
from ietf.person.models import Person, User
from ietf.utils.test_data import make_test_data


SECR_USER='secretary'

class RolodexTestCase(TestCase):
    def test_main(self):
        "Main Test"
        url = reverse('ietf.secr.rolodex.views.search')
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view(self):
        "View Test"
        make_test_data()
        person = Person.objects.all()[0]
        url = reverse('ietf.secr.rolodex.views.view', kwargs={'id':person.id})
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add(self):
        make_test_data()
        url = reverse('ietf.secr.rolodex.views.add')
        add_proceed_url = reverse('ietf.secr.rolodex.views.add_proceed') + '?name=Joe+Smith'
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, {'name':'Joe Smith'})
        self.assertRedirects(response, add_proceed_url)
        post_data = {
            'name': 'Joe Smith',
            'ascii': 'Joe Smith',
            'ascii_short': 'Joe S',
            'affiliation': 'IETF',
            'email': 'joes@exanple.com',
            'submit': 'Submit',
        }
        response = self.client.post(add_proceed_url, post_data)
        person = Person.objects.get(name='Joe Smith')
        view_url = reverse('ietf.secr.rolodex.views.view', kwargs={'id':person.pk})
        self.assertRedirects(response, view_url)

    def test_edit_replace_user(self):
        person = PersonFactory()
        user = UserFactory()
        url = reverse('ietf.secr.rolodex.views.edit', kwargs={'id':person.id})
        redirect_url = reverse('ietf.secr.rolodex.views.view', kwargs={'id':person.id})
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        post_data = {
            'name': person.name,
            'ascii': person.ascii,
            'ascii_short': person.ascii_short,
            'affiliation': person.affiliation,
            'user': user.username,
            'email-0-person':person.pk,
            'email-0-address': person.email_address(),
            'email-TOTAL_FORMS':1,
            'email-INITIAL_FORMS':1,
            'email-MIN_NUM_FORMS':0,
            'email-MAX_NUM_FORMS':1000,
            'submit': 'Submit',
        }
        original_user = person.user
        person_id = person.pk
        response = self.client.post(url, post_data, follow=True)
        person = Person.objects.get(id=person_id)
        original_user = User.objects.get(id=original_user.id)
        self.assertRedirects(response, redirect_url)
        self.assertEqual(person.user, user)
        self.assertTrue(not original_user.is_active)
