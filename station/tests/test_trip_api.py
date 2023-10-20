from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from station.models import Station, Route, TrainType, Train, Crew, Trip
from station.serializers import TripListSerializer, TripDetailSerializer

TRIP_URL = reverse("station:trip-list")


def sample_station(**params):
    defaults = {
        "name": "Station",
        "latitude": 38.0753009,
        "longitude": 43.5792084
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


def sample_route(**params):
    defaults = {
        "source": sample_station(),
        "destination": sample_station(),
        "distance": 100
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_train_type(**params):
    defaults = {
        "name": "Train Type"
    }
    defaults.update(params)

    return TrainType.objects.create(**defaults)


def sample_train(**params):
    defaults = {
        "name": "Train",
        "train_type": sample_train_type(),
        "cargo_num": 9,
        "places_in_cargo": 45
    }
    defaults.update(params)

    train = Train.objects.create(**defaults)

    return train


def sample_crew(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Doe",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def sample_trip(**params):
    defaults = {
        "train": sample_train(),
        "route": sample_route(),
        "departure_time": datetime(2022, 6, 2, 14, 0),
        "arrival_time": datetime(2022, 6, 2, 16, 0)
    }
    defaults.update(params)

    return Trip.objects.create(**defaults)


def detail_url(trip_id):
    return reverse("station:trip-detail", args=[trip_id])


class UnauthenticatedTripApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRIP_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTripApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            password="password123",
        )
        self.client.force_authenticate(self.user)

    def test_list_trips(self):
        sample_trip()

        res = self.client.get(TRIP_URL)

        trips = Trip.objects.annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo")
                - Count("tickets")
            )
        ).order_by("-departure_time")
        serializer = TripListSerializer(trips, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_trips_by_source(self):
        trip1 = sample_trip()
        trip2 = sample_trip()
        trip3 = sample_trip()

        trip1.route.source.name = "Kyiv"
        trip1.route.source.save()

        res = self.client.get(TRIP_URL, {"source": "Kyiv"})

        serializer1 = TripListSerializer(trip1)
        serializer2 = TripListSerializer(trip2)
        serializer3 = TripListSerializer(trip3)

        self.assertEqual(serializer1.data["id"], res.data[0]["id"])
        self.assertNotIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_trips_by_destination(self):
        trip1 = sample_trip()
        trip2 = sample_trip()
        trip3 = sample_trip()

        trip2.route.destination.name = "Lviv"
        trip2.route.destination.save()

        res = self.client.get(TRIP_URL, {"destination": "Lviv"})

        serializer1 = TripListSerializer(trip1)
        serializer2 = TripListSerializer(trip2)
        serializer3 = TripListSerializer(trip3)

        self.assertNotIn(serializer1.data, res.data)
        self.assertEqual(serializer2.data["id"], res.data[0]["id"])
        self.assertNotIn(serializer3.data, res.data)

    def test_retrieve_trip_detail(self):
        trip = sample_trip()

        url = detail_url(trip.id)
        res = self.client.get(url)

        serializer = TripDetailSerializer(trip)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_trip_forbidden(self):
        payload = {
            "train": sample_train(),
            "route": sample_route(),
            "departure_time": datetime(2022, 6, 2, 14, 0),
            "arrival_time": datetime(2022, 6, 2, 16, 0),
        }

        res = self.client.post(TRIP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_trip_forbidden(self):
        trip = sample_trip()
        url = detail_url(trip.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@gmail.com",
            password="admin"
        )
        self.client.force_authenticate(self.user)

    def test_create_trip(self):
        payload = {
            "train": sample_train().id,
            "route": sample_route().id,
            "departure_time": datetime(2022, 6, 2, 14, 0),
            "arrival_time": datetime(2022, 6, 2, 16, 0),
            "crews": [sample_crew().id, sample_crew().id],
        }

        res = self.client.post(TRIP_URL, payload)

        trip = Trip.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(payload["departure_time"], trip.departure_time)
        self.assertEqual(payload["arrival_time"], trip.arrival_time)

        self.assertEqual(payload["train"], trip.train.id)
        self.assertEqual(payload["route"], trip.route.id)
        self.assertEqual(payload["crews"][0], trip.crews.all()[0].id)
        self.assertEqual(payload["crews"][1], trip.crews.all()[1].id)

    def test_put_trip(self):
        payload = {
            "train": sample_train().id,
            "route": sample_route().id,
            "departure_time": datetime(2022, 6, 2, 14, 0),
            "arrival_time": datetime(2022, 6, 2, 16, 0),
            "crews": [sample_crew().id, sample_crew().id],
        }

        trip = sample_trip()
        url = detail_url(trip.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_trip(self):
        trip = sample_trip()
        url = detail_url(trip.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
