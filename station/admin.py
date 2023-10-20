from django.contrib import admin

from .models import (
    TrainType,
    Train,
    Station,
    Route,
    Crew,
    Trip,
    Order,
    Ticket,
)

admin.site.register(TrainType)
admin.site.register(Train)
admin.site.register(Station)
admin.site.register(Route)
admin.site.register(Crew)
admin.site.register(Trip)
admin.site.register(Order)
admin.site.register(Ticket)
