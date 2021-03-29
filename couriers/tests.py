from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from collections import OrderedDict
import datetime

from couriers.models import *


class BasicTest(TestCase):
    def test_fields(self):
        courier = Courier()
        courier.courier_id = 1
        courier.courier_type = 'bike'
        courier.regions = [1, 2, 3, 4]
        courier.working_hours = ['08:00-13:00', '16:00-18:00']
        courier.save()
        record = Courier.objects.get(pk=courier.courier_id)
        self.assertEqual(record, courier)
        order = Order()
        order.order_id = 100
        order.weight = 9.81
        order.region = 4
        order.delivery_hours = ["08:00-18:00"]
        order.save()
        record = Order.objects.get(pk=order.order_id)
        self.assertEqual(record, order)


class ApiTestCase(APITestCase):
    def test_api(self):
        # Test 1: Courier create
        url = '/couriers'
        data = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 2,
                    "courier_type": "bike",
                    "regions": [22],
                    "working_hours": ["09:00-18:00"]
                },
                {
                    "courier_id": 3,
                    "courier_type": "car",
                    "regions": [12, 22, 23, 33],
                    "working_hours": []
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        correct = {'couriers': [{'id': i} for i in range(1, 4)]}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, correct)

        # Test 2: Courier patch
        url = '/couriers/3'
        data = {
            'regions': [1, 12, 22, 23, 33],
            'working_hours': ['04:00-13:00', '18:00-22:00']
        }
        response = self.client.patch(url, data, format='json')
        correct = {
            'courier_id': 3,
            'courier_type': 'car',
            'regions': [1, 12, 22, 23, 33],
            'working_hours': ['04:00-13:00', '18:00-22:00']
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, correct)

        # Test 3: Order create
        url = '/orders'
        data = {
            "data": [
                {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 2,
                    "weight": 15,
                    "region": 1,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        correct = {
            'orders': [{'id': i} for i in range(1, 4)]
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, correct)

        # Test 4: Order assign
        url = '/orders/assign'
        data = {
            "courier_id": 3
        }
        correct = {
            'orders': [{'id': i} for i in range(1, 4)]
        }
        response = self.client.post(url, data, format='json')
        response.data.pop('assign_time')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, correct)

        # Test 5: Order complete
        url = '/orders/complete'
        data = {
            "courier_id": 3,
            "order_id": 1,
            "complete_time": datetime.datetime.utcnow().isoformat()
        }
        print(data['complete_time'])
        correct = {
            'order_id': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, correct)

        # Test 6: Get courier information
        url = '/couriers/3'
        correct = {
            'courier_id': 3,
            'courier_type': 'car',
            'regions': [1, 12, 22, 23, 33],
            'working_hours': ['04:00-13:00', '18:00-22:00'],
            'rating': 5.0,
            'earnings': 4500,
        }
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, correct)
