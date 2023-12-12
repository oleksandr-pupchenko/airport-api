from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Route, Airplane, Flight, Airport
from airport.serializers import RouteListSerializer, RouteDetailSerializer

ROUTE_URL = reverse("airport:route-list")


def detail_url(route_id):
    return reverse("airport:route-detail", args=[route_id])


def sample_route(**params):
    source = Airport.objects.create(
        name="Test-1234", closest_big_city="Kyiv"
    )
    destination = Airport.objects.create(
        name="Test-5678", closest_big_city="Lisbon"
    )
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 2000,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_routes(self):
        sample_route()

        res = self.client.get(ROUTE_URL)

        routes = Route.objects.order_by("id")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_route_detail(self):
        route = sample_route()

        url = detail_url(route.id)
        res = self.client.get(url)

        serializer = RouteDetailSerializer(route)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        payload = {
            "source": "Source",
            "destination": "Destination",
            "distance": 1000,
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route_with_source_and_destination(self):
        source = Airport.objects.create(
            name="Test-1", closest_big_city="Kyiv"
        )
        destination = Airport.objects.create(
            name="Test-2", closest_big_city="Lisbon"
        )
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 1000,
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        route = Route.objects.get(id=res.data["id"])

        source_airport = route.source
        destination_airport = route.destination

        self.assertEqual(source_airport.name, "Test-1")
        self.assertEqual(destination_airport.name, "Test-2")
