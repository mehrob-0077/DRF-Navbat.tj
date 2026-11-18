from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer


class BookingList(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user) | Booking.objects.filter(branch__organization__owner=self.request.user)


class BookingCreate(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        branch = serializer.validated_data['branch']
        date = serializer.validated_data['appointment_date']
        time = serializer.validated_data['appointment_time']
        if date < timezone.localdate():
            raise ValidationError({'appointment_date': 'Past dates cannot be booked.'})
        if Booking.objects.filter(branch=branch,appointment_date=date,appointment_time=time,).exclude(status=Booking.STATUS_CANCELLED).exists():
            raise ValidationError({'appointment_time': 'This time is already booked.'})
        serializer.save(user=self.request.user, status=Booking.STATUS_PENDING)


class BookingDetail(generics.RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user) | Booking.objects.filter(branch__organization__owner=self.request.user)


class BookingUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user) | Booking.objects.filter(branch__organization__owner=self.request.user)

    def perform_update(self, serializer):
        booking = self.get_object()
        is_manager = booking.branch.organization.owner == self.request.user or self.request.user.is_staff

        if not is_manager and (booking.user != self.request.user or serializer.validated_data != {'status': Booking.STATUS_CANCELLED}):
            raise PermissionDenied('You can only cancel your own booking.')

        branch = serializer.validated_data.get('branch', booking.branch)
        date = serializer.validated_data.get('appointment_date', booking.appointment_date)
        time = serializer.validated_data.get('appointment_time', booking.appointment_time)

        if date < timezone.localdate():
            raise ValidationError({'appointment_date': 'Past dates cannot be booked.'})

        if Booking.objects.filter(branch=branch,appointment_date=date,appointment_time=time,).exclude(status=Booking.STATUS_CANCELLED).exclude(pk=booking.pk).exists():
            raise ValidationError({'appointment_time': 'This time is already booked.'})
        serializer.save()

class BookingDelete(generics.DestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user) | Booking.objects.filter(branch__organization__owner=self.request.user)

    def perform_destroy(self, instance):
        raise ValidationError('Bookings are kept for history. Cancel the booking instead.')
