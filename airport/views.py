import datetime

from django.db.models import F, Count
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Route, Order
)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import (
    AirportSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    CrewSerializer,
    FlightSerializer,
    FlightListSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    FlightDetailSerializer,
    OrderSerializer,
    OrderListSerializer
)


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        source_id_str = self.request.query_params.get("source")
        destination_id_str = self.request.query_params.get("destination")

        queryset = self.queryset

        if source_id_str:
            queryset = queryset.filter(source_id=int(source_id_str))

        if destination_id_str:
            queryset = queryset.filter(destination_id=int(destination_id_str))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return super().get_serializer_class()


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .select_related("route", "airplane")
        .prefetch_related("crews")
        .annotate(
            tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row")
                    - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        departure_date = self.request.query_params.get("departure_date")
        arrival_date = self.request.query_params.get("arrival_date")
        airplane_id_str = self.request.query_params.get("airplane")

        queryset = self.queryset

        if departure_date:
            departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_date__date=departure_date)

        if arrival_date:
            arrival_date = datetime.strptime(arrival_date, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_date__date=arrival_date)

        if airplane_id_str:
            queryset = queryset.filter(movie_id=int(airplane_id_str))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return super().get_serializer_class()


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route", "tickets__flight__airplane"
    )
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
