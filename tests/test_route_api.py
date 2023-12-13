from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Route, Airport
from airport.serializers import RouteListSerializer, RouteDetailSerializer

ROUTE_URL = reverse("airport:route-list")


def sample_airport(name, closest_big_city):
    return Airport.objects.create(name=name, closest_big_city=closest_big_city)


def sample_route(source, destination, distance):
    return Route.objects.create(source=source, destination=destination, distance=distance)


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
        source = sample_airport("Test-1", "Kyiv")
        destination = sample_airport("Test-2", "Lisbon")
        sample_route(source, destination, 1000)

        res = self.client.get(ROUTE_URL)

        routes = Route.objects.select_related("source", "destination").order_by("id")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        source = sample_airport("Test-1", "Kyiv")
        destination = sample_airport("Test-2", "Lisbon")

        payload = {
            "source": source.id,
            "destination": destination.id,
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

    def test_create_route(self):
        source = sample_airport("Test-1", "Kyiv")
        destination = sample_airport("Test-2", "Lisbon")

        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 1000,
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_filter_routes_by_source(self):
        source1 = sample_airport("Test-1", "Kyiv")
        source2 = sample_airport("Test-3", "Moscow")
        destination = sample_airport("Test-2", "Lisbon")
        sample_route(source1, destination, 1000)
        sample_route(source2, destination, 1500)

        res = self.client.get(ROUTE_URL, {"source": source1.id})

        routes = Route.objects.select_related("source", "destination").filter(source=source1).order_by("id")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_routes_by_destination(self):
        source = sample_airport("Test-1", "Kyiv")
        destination1 = sample_airport("Test-2", "Lisbon")
        destination2 = sample_airport("Test-4", "Barcelona")
        sample_route(source, destination1, 1000)
        sample_route(source, destination2, 1500)

        res = self.client.get(ROUTE_URL, {"destination": destination1.id})

        routes = Route.objects.select_related("source", "destination").filter(destination=destination1).order_by("id")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_route_detail(self):
        source = sample_airport("Test-1", "Kyiv")
        destination = sample_airport("Test-2", "Lisbon")
        route = sample_route(source, destination, 1000)

        url = reverse("airport:route-detail", args=[route.id])
        res = self.client.get(url)

        serializer = RouteDetailSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
