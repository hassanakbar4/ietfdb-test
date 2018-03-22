# -*- coding: utf-8 -*-
import datetime
from pyquery import PyQuery

import debug    # pyflakes:ignore

from django.urls import reverse

from ietf.doc.models import Document, State, BallotDocEvent, BallotType, BallotPositionDocEvent
from ietf.doc.utils import update_telechat, create_ballot_if_not_open
from ietf.utils.test_utils import TestCase
from ietf.iesg.models import TelechatDate
from ietf.person.models import Person
from ietf.secr.telechat.views import get_next_telechat_date
from ietf.utils.test_data import make_test_data

SECR_USER='secretary'

def augment_data():
    TelechatDate.objects.create(date=datetime.datetime.today())

class SecrTelechatTestCase(TestCase):
    def test_main(self):
        "Main Test"
        augment_data()
        url = reverse('ietf.secr.telechat.views.main')
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_doc(self):
        "View Test"
        augment_data()
        d = TelechatDate.objects.all()[0]
        date = d.date.strftime('%Y-%m-%d')
        url = reverse('ietf.secr.telechat.views.doc', kwargs={'date':date})
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_doc_detail_draft(self):
        draft = make_test_data()
        ad = Person.objects.get(user__username="ad")
        create_ballot_if_not_open(None, draft, ad, 'approve')
        d = get_next_telechat_date()
        date = d.strftime('%Y-%m-%d')
        by=Person.objects.get(name="(System)")
        update_telechat(None, draft, by, d)
        url = reverse('ietf.secr.telechat.views.doc_detail', kwargs={'date':date, 'name':draft.name})
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        q = PyQuery(response.content)
        self.assertEqual(q("#telechat-positions-table").find("th:contains('Yes')").length,1)
        self.assertEqual(q("#telechat-positions-table").find("th:contains('No Objection')").length,1)
        self.assertEqual(q("#telechat-positions-table").find("th:contains('Discuss')").length,1)
        self.assertEqual(q("#telechat-positions-table").find("th:contains('Abstain')").length,1)
        self.assertEqual(q("#telechat-positions-table").find("th:contains('Recuse')").length,1)
        self.assertEqual(q("#telechat-positions-table").find("th:contains('No Record')").length,1)

    def test_doc_detail_draft_invalid(self):
        '''Test using a document not on telechat agenda'''
        draft = make_test_data()
        date = get_next_telechat_date().strftime('%Y-%m-%d')
        url = reverse('ietf.secr.telechat.views.doc_detail', kwargs={'date':date, 'name':draft.name})
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('ietf.secr.telechat.views.doc', kwargs={'date':date}))
        self.assertTrue('not on the Telechat agenda' in response.content)

    def test_doc_detail_charter(self):
        make_test_data()
        by=Person.objects.get(name="(System)")
        charter = Document.objects.filter(type='charter').first()
        charter.set_state(State.objects.get(used=True, slug="intrev", type="charter"))
        last_week = datetime.date.today()-datetime.timedelta(days=7)
        BallotDocEvent.objects.create(type='created_ballot',by=by,doc=charter, rev=charter.rev,
                                      ballot_type=BallotType.objects.get(doc_type=charter.type,slug='r-extrev'),
                                      time=last_week)
        d = get_next_telechat_date()
        date = d.strftime('%Y-%m-%d')
        update_telechat(None, charter, by, d)
        url = reverse('ietf.secr.telechat.views.doc_detail', kwargs={'date':date, 'name':charter.name})
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        q = PyQuery(response.content)
        self.assertEqual(q("#telechat-positions-table").find("th:contains('Yes')").length,1)
        self.assertEqual(q("#telechat-positions-table").find("th:contains('No Objection')").length,1)
        self.assertEqual(q("#telechat-positions-table").find("th:contains('Block')").length,1)
        self.assertEqual(q("#telechat-positions-table").find("th:contains('Abstain')").length,1)
        self.assertEqual(q("#telechat-positions-table").find("th:contains('No Record')").length,1)

    def test_bash(self):
        today = datetime.datetime.today() 
        TelechatDate.objects.create(date=today)
        url = reverse('ietf.secr.telechat.views.bash',kwargs={'date':today.strftime('%Y-%m-%d')})
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_doc_detail_post_update_ballot(self):
        make_test_data()
        by=Person.objects.get(name="(System)")
        charter = Document.objects.filter(type='charter').first()
        charter.set_state(State.objects.get(used=True, slug="intrev", type="charter"))
        last_week = datetime.date.today()-datetime.timedelta(days=7)
        BallotDocEvent.objects.create(type='created_ballot',by=by,doc=charter, rev=charter.rev,
                                      ballot_type=BallotType.objects.get(doc_type=charter.type,slug='r-extrev'),
                                      time=last_week)
        d = get_next_telechat_date()
        date = d.strftime('%Y-%m-%d')
        update_telechat(None, charter, by, d)
        url = reverse('ietf.secr.telechat.views.doc_detail', kwargs={'date':date, 'name':charter.name})
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url,{
                'submit': 'update_ballot',
                'form-INITIAL_FORMS':7,
                'form-TOTAL_FORMS':7,
                'form-0-name': 'Ops Ad', 
                'form-0-id': '13', 
                'form-0-position': 'noobj',
                'form-1-name': 'Areað Irector',
                'form-1-id': '12', 
                'form-2-name': 'Ad No1', 
                'form-2-id': '16',
                'form-3-name': 'Ad No2',
                'form-3-id': '17',
                'form-4-name': 'Ad No3',
                'form-4-id': '18',
                'form-5-name': 'Ad No4',
                'form-5-id': '19',
                'form-6-name': 'Ad No5',
                'form-6-id': '20',
            }
        )
        self.assertEqual(response.status_code,302)
        self.assertTrue(BallotPositionDocEvent.objects.filter(doc=charter, ad_id=13, pos__slug='noobj').exists())

    def test_doc_detail_post_update_state(self):
        make_test_data()
        by=Person.objects.get(name="(System)")
        charter = Document.objects.filter(type='charter').first()
        charter.set_state(State.objects.get(used=True, slug="intrev", type="charter"))
        last_week = datetime.date.today()-datetime.timedelta(days=7)
        BallotDocEvent.objects.create(type='created_ballot',by=by,doc=charter, rev=charter.rev,
                                      ballot_type=BallotType.objects.get(doc_type=charter.type,slug='r-extrev'),
                                      time=last_week)
        d = get_next_telechat_date()
        date = d.strftime('%Y-%m-%d')
        update_telechat(None, charter, by, d)
        url = reverse('ietf.secr.telechat.views.doc_detail', kwargs={'date':date, 'name':charter.name})
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url,{
                 'submit': 'update_state',
                 'state': 83, 
                 'substate': '',
            }
        )
        self.assertEqual(response.status_code,302)
        self.assertEqual(charter.get_state('charter').slug,'notrev')
