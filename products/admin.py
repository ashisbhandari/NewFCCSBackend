from django.contrib import admin
from .models import Shipment, Sender, Receiver, ShipmentPiece, ShipmentTracking


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'packet_type', 'destination_district', 'total_price', 'created_at')
    search_fields = ('product_id',)
    list_filter = ('packet_type', 'destination_district')


@admin.register(ShipmentTracking)
class ShipmentTrackingAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'status', 'location', 'timestamp', 'updated_by')
    search_fields = ('shipment__product_id', 'status', 'location')
    list_filter = ('status', 'timestamp')
    readonly_fields = ('timestamp',)


admin.site.register(Sender)
admin.site.register(Receiver)
admin.site.register(ShipmentPiece)
