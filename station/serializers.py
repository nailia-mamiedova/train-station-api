from django.db import transaction
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
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type", "capacity")


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


class RouteDetailSerializer(RouteSerializer):
    coordinates_source = serializers.CharField(source="source.coordinates")
    coordinates_destination = serializers.CharField(source="destination.coordinates")

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "coordinates_source",
            "destination",
            "coordinates_destination",
            "distance"
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crews")


class TripListSerializer(TripSerializer):
    route_source = serializers.CharField(source="route.source.name")
    route_destination = serializers.CharField(source="route.destination.name")
    train = serializers.CharField(source="train.name")
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Trip
        fields = (
            "id",
            "route_source",
            "route_destination",
            "train",
            "departure_time",
            "arrival_time",
            "tickets_available"
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_cargo(attrs["cargo"], attrs["trip"].train.cargo_num, serializers.ValidationError)
        Ticket.validate_seat(attrs["seat"], attrs["trip"].train.places_in_cargo, serializers.ValidationError)

        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "trip")


class TicketSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("cargo", "seat")


class TripDetailSerializer(TripSerializer):
    route = RouteSerializer()
    train = TrainSerializer()
    crews = serializers.SlugRelatedField(
        many=True, slug_field="full_name", queryset=Crew.objects.all()
    )
    taken_seats = TicketSeatSerializer(many=True, read_only=True, source="tickets")

    class Meta:
        model = Trip
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crews",
            "taken_seats"
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order
