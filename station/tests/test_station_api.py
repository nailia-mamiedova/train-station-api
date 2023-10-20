from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from station.models import Station
from station.serializers import StationSerializer

STATION_URL = reverse("station:station-list")


def sample_station(**params):
    defaults = {
        "name": "Station",
        "latitude": 38.0753009,
        "longitude": 43.5792084
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


class UnauthenticatedStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(STATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            password="password123",
        )
        self.client.force_authenticate(self.user)

    def test_list_stations(self):
        sample_station()
        sample_station()

        res = self.client.get(STATION_URL)

        stations = Station.objects.all().order_by("id")
        serializer = StationSerializer(stations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_station_forbidden(self):
        payload = {
            "name": "Station",
            "latitude": 29.8758920,
            "longitude": 41.573920
        }

        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@gmail.com",
            password="admin"
        )
        self.client.force_authenticate(self.user)

    def test_create_station(self):
        payload = {
            "name": "Station",
            "latitude": 29.8758920,
            "longitude": 41.573920
        }

        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        station = Station.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(station, key))
