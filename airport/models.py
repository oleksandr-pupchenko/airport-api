from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Airport(models.Model):
    name = models.CharField(max_length=255, unique=True)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


def different_airports_validator(value):
    if value.source == value.destination:
        raise ValidationError("Source and destination airports must be different.")


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="outgoing_routes")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="incoming_routes")
    distance = models.IntegerField()

    def __str__(self):
        return f"Flight from {self.source} to {self.destination}. " \
               f"Estimated distance is {self.distance}."

    def clean(self):
        different_airports_validator(self)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255, blank=False)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField(Crew, blank=True)

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return str(self.departure_time) + "-" + str(self.arrival_time)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]
