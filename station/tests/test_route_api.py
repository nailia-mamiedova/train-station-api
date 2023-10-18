from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from station.models import Station, Route
from station.serializers import (
    RouteDetailSerializer,
    RouteListSerializer
)

ROUTE_URL = reverse("station:route-list")


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


def detail_url(route_id):
    return reverse("station:route-detail", args=[route_id])


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            password="password123",
        )
        self.client.force_authenticate(self.user)

    def test_list_routers(self):
        sample_route()
        sample_route()

        res = self.client.get(ROUTE_URL)

        routers = Route.objects.all().order_by("id")
        serializer = RouteListSerializer(routers, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_route_detail(self):
        route = sample_route()

        url = detail_url(route.id)
        res = self.client.get(url)

        serializer = RouteDetailSerializer(route)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        payload = {
            "source": sample_station(),
            "destination": sample_station(),
            "distance": 100
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_route_list_source_and_destination(self):
        route = sample_route()
        source = route.source.name
        destination = route.destination.name

        res = self.client.get(ROUTE_URL)
        res_source = res.data[0]["source"]
        res_destination = res.data[0]["destination"]

        self.assertEqual(source, res_source)
        self.assertEqual(destination, res_destination)

    def test_route_retrieve_source_and_destination_coordination(self):
        route = sample_route()

        source_coordination = route.source.coordinates
        destination_coordination = route.destination.coordinates

        url = detail_url(route.id)

        res = self.client.get(url)

        res_source_coordination = res.data["coordinates_source"]
        res_destination_coordination = res.data["coordinates_destination"]

        self.assertEqual(source_coordination, res_source_coordination)
        self.assertEqual(destination_coordination, res_destination_coordination)


class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@gmail.com",
            password="admin"
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        payload = {
            "source": sample_station().id,
            "destination": sample_station().id,
            "distance": 100
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        route = Route.objects.get(id=res.data["id"])

        self.assertEqual(payload["source"], route.source.id)
        self.assertEqual(payload["destination"], route.destination.id)
        self.assertEqual(payload["distance"], route.distance)

    def test_put_route_not_allowed(self):
        payload = {
            "source": sample_station(),
            "destination": sample_station(),
            "distance": 110
        }

        route = sample_route()
        url = detail_url(route.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_route_not_allowed(self):
        route = sample_route()
        url = detail_url(route.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
