from django.urls import path, include
from rest_framework import routers

from station.views import (
    TrainTypesViewSet,
    TrainViewSet,
    StationViewSet,
    RouteViewSet,
    CrewViewSet,
    TripViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()
router.register("train_types", TrainTypesViewSet)
router.register("trains", TrainViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("trips", TripViewSet)
router.register("orders", OrderViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "station"
