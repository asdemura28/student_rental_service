from django.urls import path
from . import views

app_name = 'bookings'  

urlpatterns = [
    path('<int:product_id>/create/', views.create_booking, name='create_booking'),
    path('my/', views.my_bookings, name='my_bookings'),
    path('owner-requests/', views.owner_requests, name='owner_requests'),
    path('<int:booking_id>/review/', views.leave_review, name='leave_review'),
]