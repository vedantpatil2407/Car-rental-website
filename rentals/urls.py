from django.urls import path
from . import views

urlpatterns = [
    # Core public pages & guest fleet exploration
    path('', views.home_view, name='home'),
    path('cars/', views.cars_list_view, name='cars_list'),
    path('cars/<int:car_id>/', views.car_detail_view, name='car_detail'),

    # Guest Booking Flow & Customer Reviews
    path('cars/<int:car_id>/book/', views.booking_form_view, name='booking_form'),
    path('cars/<int:car_id>/review/', views.submit_car_review_view, name='submit_car_review'),
    path('booking/submit/', views.booking_submit_view, name='booking_submit'),
    path('booking/lookup/', views.booking_lookup_view, name='booking_lookup'),
    path('booking/<str:booking_ref>/voucher/', views.booking_voucher_view, name='booking_voucher'),
    path('booking/<str:booking_ref>/cancel/', views.cancel_booking_view, name='cancel_booking'),

    # Informational & Policy Pages
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    path('rental-policy/', views.rental_policy_view, name='rental_policy'),
    path('rental-rules/', views.rental_rules_view, name='rental_rules'),
    path('privacy/', views.privacy_view, name='privacy'),

    # Owner Authentication & Admin Portal (Staff / Operations)
    path('owner/login/', views.owner_login_view, name='owner_login'),
    path('owner/logout/', views.owner_logout_view, name='owner_logout'),
    path('admin-portal/', views.admin_shell_preview_view, name='admin_shell_preview'),
    path('admin-portal/cars/', views.admin_manage_cars_view, name='admin_manage_cars'),
    path('admin-portal/cars/add/', views.admin_car_create_view, name='admin_car_add'),
    path('admin-portal/cars/<int:car_id>/edit/', views.admin_car_edit_view, name='admin_car_edit'),
    path('admin-portal/cars/<int:car_id>/delete/', views.admin_car_delete_view, name='admin_car_delete'),
]
