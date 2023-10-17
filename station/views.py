from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from station.models import (
    TrainType,
    Train,
    Station,
    Route,
    Crew,
    Trip,
    Order,
)
from station.permissions import IsAdminOrIfAuthenticatedReadOnly
from station.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
    StationSerializer,
    RouteSerializer,
    CrewSerializer,
    TripSerializer,
    OrderSerializer,
    TripListSerializer,
    TripDetailSerializer,
    RouteDetailSerializer,
    OrderListSerializer,
)


class TrainTypesViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related(
        "route__source", "route__destination"
    ).annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo")
                - Count("tickets")
            )
        )
    serializer_class = TripSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "retrieve":
            queryset = queryset.select_related("train__train_type").prefetch_related("crews")

        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        departure_time = self.request.query_params.get("departure_time")
        arrival_time = self.request.query_params.get("arrival_time")

        if departure_time:
            departure_time = datetime.strptime(departure_time, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=departure_time)

        if arrival_time:
            arrival_time = datetime.strptime(arrival_time, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=arrival_time)

        if source:
            queryset = queryset.filter(route__source__name__icontains=source)

        if destination:
            queryset = queryset.filter(route__destination__name__icontains=destination)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer

        if self.action == "retrieve":
            return TripDetailSerializer

        return TripSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by source station (ex. ?source=Kiev)",
                examples=[
                    OpenApiExample(
                        "Example",
                        value="Kyiv",
                    )
                ],
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter by destination station (ex. ?destination=Lviv)",
                examples=[
                    OpenApiExample(
                        "Example",
                        value="Lviv",
                    )
                ]
            ),
            OpenApiParameter(
                "departure_time",
                type=OpenApiTypes.DATE,
                description="Filter by departure date (ex. ?departure_time=2023-10-31)",
                examples=[
                    OpenApiExample(
                        "Example",
                        value="2023-10-31",
                    )
                ]
            ),
            OpenApiParameter(
                "arrival_time",
                type=OpenApiTypes.DATE,
                description="Filter by arrival date (ex. ?arrival_time=2023-11-01)",
                examples=[
                    OpenApiExample(
                        "Example",
                        value="2023-11-01",
                    )
                ]
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
