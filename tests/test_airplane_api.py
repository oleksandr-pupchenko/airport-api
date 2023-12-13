from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneSerializer

AIRPLANE_URL = reverse("airport:airplane-list")


def sample_airplane_type(name="Boeing 737"):
    return AirplaneType.objects.create(name=name)


def sample_airplane(name="Test Airplane", rows=20, seats_in_row=6, airplane_type=None):
    if not airplane_type:
        airplane_type = sample_airplane_type()
    return Airplane.objects.create(
        name=name,
        rows=rows,
        seats_in_row=seats_in_row,
        airplane_type=airplane_type
    )


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_airplane(self):
        sample_airplane()

        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.order_by("id")
        serializer = AirplaneSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "Test",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type": sample_airplane_type().id
        }
        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        payload = {
            "name": "Test",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type": sample_airplane_type().id
        }
        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
