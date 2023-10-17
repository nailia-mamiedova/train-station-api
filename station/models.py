from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError


class TrainType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.train_type})"

    @property
    def capacity(self):
        return self.cargo_num * self.places_in_cargo

    class Meta:
        ordering = ["name"]


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],)
    longitude = models.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],)

    def __str__(self):
        return self.name

    @property
    def coordinates(self):
        return f"{self.latitude}, {self.longitude}"


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="source")
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="destination")
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} - {self.destination}"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Trip(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField(Crew)

    def __str__(self):
        return f"{str(self.route)} ({self.departure_time} - {self.arrival_time})"

    class Meta:
        ordering = ["-departure_time"]


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
    cargo = models.IntegerField()
    seat = models.IntegerField()
    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    def __str__(self):
        return f"{str(self.trip)}(cargo: {self.cargo}, seat: {self.seat})"

    class Meta:
        unique_together = ("trip", "cargo", "seat")
        ordering = ["cargo", "seat"]

    @staticmethod
    def validate_cargo(cargo: int, cargo_num: int, error_to_raise):
        if not cargo_num >= cargo >= 1:
            raise error_to_raise(
                f"Cargo number must be between 1 and {cargo_num}"
            )

    @staticmethod
    def validate_seat(seat, seat_num, error_to_raise):
        if not seat_num >= seat >= 1:
            raise error_to_raise(
                f"Seat number must be between 1 and {seat_num}"
            )

    def clean(self):
        Ticket.validate_cargo(self.cargo, self.trip.train.cargo_num, ValidationError)
        Ticket.validate_seat(self.seat, self.trip.train.places_in_cargo, ValidationError)
