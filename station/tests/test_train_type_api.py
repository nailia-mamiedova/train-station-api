from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from station.models import TrainType
from station.serializers import TrainTypeSerializer

TRAIN_TYPE_URL = reverse("station:traintype-list")


def sample_train_type(**params):
    defaults = {
        "name": "Train Type"
    }
    defaults.update(params)

    return TrainType.objects.create(**defaults)


class UnauthenticatedTrainTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            password="password123",
        )
        self.client.force_authenticate(self.user)

    def test_list_train_types(self):
        sample_train_type()
        sample_train_type()

        res = self.client.get(TRAIN_TYPE_URL)

        train_types = TrainType.objects.all().order_by("id")
        serializer = TrainTypeSerializer(train_types, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_train_type_forbidden(self):
        payload = {
            "name": "Train Type"
        }

        res = self.client.post(TRAIN_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@gmail.com",
            password="admin"
        )
        self.client.force_authenticate(self.user)

    def test_create_train_type(self):
        payload = {
            "name": "Train Type"
        }

        res = self.client.post(TRAIN_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        train_type = TrainType.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(train_type, key))
