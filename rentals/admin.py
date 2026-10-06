from django.contrib import admin
from django.utils.html import format_html
import urllib.parse
from .models import Location, Car, BookingRequest, CarReview


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active', 'maps_button', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
    list_editable = ('is_active',)

    def maps_button(self, obj):
        if obj.maps_link:
            return format_html(
                '<a href="{}" target="_blank" style="color: #00D2FF; text-decoration: underline;">View Map</a>',
                obj.maps_link
            )
        return "-"
    maps_button.short_description = "Map"


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        'brand', 'model', 'vehicle_class', 'price_per_day', 
        'security_deposit', 'transmission', 'fuel_type', 'badge', 
        'is_featured', 'is_active'
    )
    list_filter = ('vehicle_class', 'transmission', 'fuel_type', 'is_featured', 'is_active')
    search_fields = ('brand', 'model', 'badge')
    list_editable = ('price_per_day', 'is_featured', 'is_active')
    fieldsets = (
        ('Vehicle Identity', {
            'fields': ('brand', 'model', 'vehicle_class', 'badge', 'image_url', 'description')
        }),
        ('Rates & Deposits', {
            'fields': ('price_per_day', 'security_deposit', 'included_km', 'extra_km_rate')
        }),
        ('Specifications', {
            'fields': ('seats', 'fuel_type', 'transmission', 'ac_status')
        }),
        ('Status & Visibility', {
            'fields': ('is_featured', 'is_active')
        }),
    )


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = (
        'booking_ref', 'customer_name', 'customer_phone', 'car', 
        'pickup_date', 'return_date', 'total_days', 'payable_at_pickup', 
        'status_badge', 'whatsapp_status_badge', 'whatsapp_action'
    )
    list_filter = ('status', 'whatsapp_status', 'pickup_location', 'pickup_date')
    search_fields = ('booking_ref', 'customer_name', 'customer_phone', 'customer_mobile', 'customer_whatsapp', 'customer_email', 'driving_license_number', 'car__brand', 'car__model')
    readonly_fields = ('booking_ref', 'created_at', 'updated_at', 'estimated_amount', 'security_deposit', 'total_days')
    actions = ['mark_as_confirmed', 'mark_as_rejected', 'mark_whatsapp_sent']

    def status_badge(self, obj):
        colors = {
            'PENDING': '#FBBF24',
            'CONFIRMED': '#34D399',
            'REJECTED': '#F87171',
            'CANCELLED': '#9CA3AF',
            'COMPLETED': '#60A5FA',
        }
        color = colors.get(obj.status, '#CBD5E1')
        return format_html(
            '<span style="background-color: rgba(255,255,255,0.08); color: {}; padding: 4px 8px; border-radius: 4px; font-weight: 600; border: 1px solid {};">{}</span>',
            color, color, obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def whatsapp_status_badge(self, obj):
        colors = {
            'NOT_SENT': '#F59E0B',
            'SENT': '#10B981',
            'FAILED': '#EF4444',
        }
        color = colors.get(obj.whatsapp_status, '#94A3B8')
        return format_html(
            '<span style="color: {}; font-size: 0.85rem; font-weight: 500;">{}</span>',
            color, obj.get_whatsapp_status_display()
        )
    whatsapp_status_badge.short_description = "WhatsApp Sync"

    def whatsapp_action(self, obj):
        phone = ''.join(filter(str.isdigit, str(obj.customer_whatsapp)))
        msg = (
            f"Hello {obj.customer_name},\n"
            f"Thank you for choosing Keys to your freedom Self-Drive Car Rental!\n\n"
            f"Booking Ref: {obj.booking_ref}\n"
            f"Vehicle: {obj.car.brand} {obj.car.model}\n"
            f"Pickup Date: {obj.pickup_date} at {obj.pickup_time}\n"
            f"Return Date: {obj.return_date} at {obj.return_time}\n"
            f"Estimated Rental: ₹{obj.estimated_amount:,} ({obj.total_days} days)\n"
            f"Security Deposit: ₹{obj.security_deposit:,}\n"
            f"Status: {obj.get_status_display()}\n\n"
            f"Please share your driving license and Aadhaar/Passport copy to finalize your booking."
        )
        url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
        return format_html(
            '<a href="{}" target="_blank" style="background-color: #25D366; color: #fff; padding: 4px 10px; border-radius: 4px; text-decoration: none; font-size: 0.8rem; font-weight: 600; display: inline-block;">Send WA</a>',
            url
        )
    whatsapp_action.short_description = "Quick WA"

    @admin.action(description="Mark selected requests as CONFIRMED")
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='CONFIRMED')

    @admin.action(description="Mark selected requests as REJECTED")
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='REJECTED')

    @admin.action(description="Mark selected as WhatsApp SENT")
    def mark_whatsapp_sent(self, request, queryset):
        queryset.update(whatsapp_status='SENT')


@admin.register(CarReview)
class CarReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'car', 'star_display', 'trip_type', 'verified_badge', 'is_approved', 'created_at')
    list_filter = ('rating', 'trip_type', 'is_verified_renter', 'is_approved', 'car')
    search_fields = ('customer_name', 'customer_phone', 'title', 'comment', 'car__brand', 'car__model')
    list_editable = ('is_approved',)
    actions = ['approve_reviews', 'mark_as_verified']

    def star_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        color = '#F59E0B' if obj.rating >= 4 else ('#FBBF24' if obj.rating == 3 else '#EF4444')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, stars)
    star_display.short_description = "Rating"

    def verified_badge(self, obj):
        if obj.is_verified_renter:
            return format_html('<span style="color: #10B981; font-weight: 600;">✓ Verified Renter</span>')
        return format_html('<span style="color: #94A3B8;">Guest</span>')
    verified_badge.short_description = "Verification"

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Mark selected as Verified Renters")
    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified_renter=True)
