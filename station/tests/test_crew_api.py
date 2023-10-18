from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from station.models import Crew
from station.serializers import CrewSerializer

CREW_URL = reverse("station:crew-list")


def sample_crew(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Doe",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            password="password123",
        )
        self.client.force_authenticate(self.user)

    def test_list_crews(self):
        sample_crew()
        sample_crew()

        res = self.client.get(CREW_URL)

        crews = Crew.objects.all().order_by("id")
        serializer = CrewSerializer(crews, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
        }

        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@gmail.com",
            password="admin"
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self):
        payload = {
            "first_name": "Alice",
            "last_name": "Doe"
        }

        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        crew = Crew.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(crew, key))

    def test_crew_list_full_name(self):
        crew = sample_crew()
        full_name = f"{crew.first_name} {crew.last_name}"

        res = self.client.get(CREW_URL)
        res_full_name = res.data[0]["full_name"]

        self.assertEqual(full_name, res_full_name)
