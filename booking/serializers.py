from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('id', 'branch', 'user', 'appointment_date', 'appointment_time', 'status')
        read_only_fields = ('id', 'user')
