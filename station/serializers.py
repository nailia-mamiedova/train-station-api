from rest_framework import serializers

from station.models import (
    TrainType,
    Train,
    Station,
    Route,
    Crew,
    Trip,
    Order,
    Ticket,
)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    train_type = serializers.SlugRelatedField(
        slug_field="name", queryset=TrainType.objects.all()
    )

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        slug_field="name", queryset=Station.objects.all()
    )
    destination = serializers.SlugRelatedField(
        slug_field="name", queryset=Station.objects.all()
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class TripSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField(
        many=False, read_only=True
    )
    train = serializers.SlugRelatedField(
        slug_field="name", queryset=Train.objects.all()
    )
    crews = serializers.SlugRelatedField(
        slug_field="full_name", queryset=Crew.objects.all(), many=True
    )

    class Meta:
        model = Trip
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crews")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    trip = serializers.SlugRelatedField(
        slug_field="id", queryset=Trip.objects.all()
    )
    order = serializers.SlugRelatedField(
        slug_field="id", queryset=Order.objects.all()
    )

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "trip", "order")
