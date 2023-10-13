from django.conf import settings
from django.db import models


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


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='source')
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='destination')
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} - {self.destination}"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Trip(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{str(self.route)} ({self.departure_time} - {self.arrival_time})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    def __str__(self):
        return f"{str(self.trip)}(cargo: {self.cargo}, seat: {self.seat})"
