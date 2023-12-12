from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    RouteViewSet,
    CrewViewSet,
    FlightViewSet
)

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplane", AirplaneViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("flights", FlightViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
