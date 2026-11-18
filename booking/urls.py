from django.urls import path
from .views import BookingList, BookingCreate, BookingDetail, BookingUpdate, BookingDelete

urlpatterns = [
    path('', BookingList.as_view(), name='booking-list'),
    path('create/', BookingCreate.as_view(), name='booking-create'),
    path('<int:pk>/', BookingDetail.as_view(), name='booking-detail'),
    path('<int:pk>/update/', BookingUpdate.as_view(), name='booking-update'),
    path('<int:pk>/delete/', BookingDelete.as_view(), name='booking-delete'),
]
