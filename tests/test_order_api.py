from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Airport, Airplane, Route, Flight, Ticket, Order, AirplaneType

ORDER_URL = reverse("airport:order-list")
FLIGHT_URL = reverse("airport:flight-list")


def sample_user(email="test@test.com", password="testpass"):
    return get_user_model().objects.create_user(email=email, password=password)


def sample_airport(name, closest_big_city):
    return Airport.objects.create(name=name, closest_big_city=closest_big_city)


def sample_route(source, destination, distance):
    return Route.objects.create(source=source, destination=destination, distance=distance)


def sample_airplane_type(name):
    return AirplaneType.objects.create(name=name)


def sample_airplane(name, rows, seats_in_row, airplane_type):
    return Airplane.objects.create(
        name=name,
        rows=rows,
        seats_in_row=seats_in_row,
        airplane_type=airplane_type
    )


def sample_flight(route, airplane, departure_time, arrival_time):
    return Flight.objects.create(
        route=route, airplane=airplane, departure_time=departure_time, arrival_time=arrival_time
    )


def sample_ticket(row, seat, flight, order):
    return Ticket.objects.create(
        row=row,
        seat=seat,
        flight=flight,
        order=order
    )


def sample_order(user):
    return Order.objects.create(user=user)


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass"
        )
        self.client.force_authenticate(self.user)
        self.source = sample_airport("Test-1", "Kyiv")
        self.destination = sample_airport("Test-2", "Lisbon")
        self.route = sample_route(self.source, self.destination, 1000)
        self.airplane_type = sample_airplane_type("Type1")
        self.airplane = sample_airplane("Airplane-1", 10, 6, self.airplane_type)
        self.flight = sample_flight(
            self.route, self.airplane, "2023-07-25T10:00:00Z", "2023-07-25T15:00:00Z"
        )
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            flight=self.flight, row=2, seat=5, order=self.order
        )

    def test_get_order(self):
        self.client.force_authenticate(user=self.user)
        orders_response = self.client.get(ORDER_URL)
        self.assertEqual(orders_response.status_code, status.HTTP_200_OK)
        self.assertEqual(orders_response.data["count"], 1)
        order = orders_response.data["results"][0]
        self.assertEqual(len(order["tickets"]), 1)
        ticket = order["tickets"][0]
        self.assertEqual(ticket["row"], 2)
        self.assertEqual(ticket["seat"], 5)
        flight = ticket["flight"]
        self.assertEqual(flight["airplane_name"], "Airplane-1")
        self.assertEqual(flight["airplane_capacity"], 60)

    def test_flight_detail_tickets(self):
        url = reverse("airport:flight-detail", args=[self.flight.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["taken_places"][0]["row"], self.ticket.row
        )
        self.assertEqual(
            response.data["taken_places"][0]["seat"], self.ticket.seat
        )
