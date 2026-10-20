import json
from unittest.mock import patch

import requests
from django.test import TestCase

from .models import CarModel
from .populate import initiate


class DealershipFlowTests(TestCase):
    def setUp(self):
        initiate()
        self.api_down = patch('djangoapp.restapis.requests.get', side_effect=requests.RequestException())
        self.api_down.start()
        self.addCleanup(self.api_down.stop)

    def test_dealers_filter_and_car_models(self):
        all_dealers = self.client.get('/djangoapp/get_dealers').json()['dealers']
        texas = self.client.get('/djangoapp/get_dealers/Texas').json()['dealers']
        self.assertGreater(len(all_dealers), len(texas))
        self.assertTrue(all(item['state'] == 'Texas' for item in texas))
        self.assertEqual(len(self.client.get('/djangoapp/get_cars').json()['CarModels']), CarModel.objects.count())

    def test_register_login_review_and_logout(self):
        user = {'userName': 'student', 'firstName': 'Test', 'lastName': 'Learner',
                'email': 'student@example.org', 'password': 'ExamplePass123!'}
        response = self.client.post('/djangoapp/register', data=json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['status'], 'Authenticated')
        review = {'dealership': 1, 'review': 'Excellent friendly service', 'purchase': True,
                  'purchase_date': '2023-06-01', 'car_make': 'Audi', 'car_model': 'A4', 'car_year': 2020}
        with patch('djangoapp.restapis.requests.post', side_effect=requests.RequestException()):
            response = self.client.post('/djangoapp/add_review', data=json.dumps(review), content_type='application/json')
        self.assertEqual(response.json()['sentiment'], 'positive')
        self.assertTrue(any(item['name'] == 'Test Learner' for item in self.client.get('/djangoapp/reviews/dealer/1').json()['reviews']))
        self.assertEqual(self.client.get('/djangoapp/logout').json()['status'], 'Logged out')
        self.assertEqual(self.client.post('/djangoapp/add_review', data=json.dumps(review), content_type='application/json').status_code, 401)
        login = self.client.post('/djangoapp/login', data=json.dumps({'userName': 'student', 'password': user['password']}), content_type='application/json')
        self.assertEqual(login.json()['status'], 'Authenticated')
