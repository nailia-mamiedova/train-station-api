from rest_framework import viewsets

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
from station.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
    StationSerializer,
    RouteSerializer,
    CrewSerializer,
    TripSerializer,
    OrderSerializer,
    TicketSerializer,
    TripListSerializer,
    TripDetailSerializer,
)


class TrainTypesViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related("route__source", "route__destination")
    serializer_class = TripSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "retrieve":
            queryset = queryset.select_related("train__train_type").prefetch_related("crews")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer

        if self.action == "retrieve":
            return TripDetailSerializer

        return TripSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
