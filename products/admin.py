from django.contrib import admin
from .models import Shipment, Sender, Receiver, ShipmentPiece


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'packet_type', 'destination_district', 'total_price', 'created_at')
    search_fields = ('product_id',)
    list_filter = ('packet_type', 'destination_district')


admin.site.register(Sender)
admin.site.register(Receiver)
admin.site.register(ShipmentPiece)
