from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from station.models import Train, TrainType
from station.serializers import TrainSerializer

TRAIN_URL = reverse("station:train-list")


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
        "cargo_num": 10,
        "places_in_cargo": 50
    }
    defaults.update(params)

    return Train.objects.create(**defaults)


class UnauthenticatedTrainApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            password="password123",
        )
        self.client.force_authenticate(self.user)

    def test_list_trains(self):
        sample_train()
        sample_train()

        res = self.client.get(TRAIN_URL)

        trains = Train.objects.all().order_by("id")
        serializer = TrainSerializer(trains, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_train_forbidden(self):
        payload = {
            "name": "Train",
            "cargo_num": 9,
            "places_in_cargo": 60,
            "train_type": sample_train_type()
        }

        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@gmail.com",
            password="admin"
        )
        self.client.force_authenticate(self.user)

    def test_create_train(self):
        payload = {
            "name": "Train",
            "cargo_num": 9,
            "places_in_cargo": 60,
            "train_type": sample_train_type()
        }

        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        train = Train.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(train, key))

    def test_train_list_capacity(self):
        train = sample_train()
        capacity = train.cargo_num * train.places_in_cargo

        res = self.client.get(TRAIN_URL)
        res_capacity = res.data[0]["capacity"]

        self.assertEqual(capacity, res_capacity)

    def test_train_list_train_type_name(self):
        train = sample_train()
        train_type_name = train.train_type.name

        res = self.client.get(TRAIN_URL)
        res_train_type_name = res.data[0]["train_type"]

        self.assertEqual(train_type_name, res_train_type_name)
