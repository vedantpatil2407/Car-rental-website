import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date


class CustomerProfile(models.Model):
    """Optional user profile for staff or admin accounts (deprecated for guests)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, default="", help_text="Mobile contact number")
    whatsapp_number = models.CharField(max_length=20, blank=True, default="", help_text="WhatsApp number for updates")
    driving_license_number = models.CharField(max_length=50, blank=True, default="", help_text="Driving License ID")
    city = models.CharField(max_length=100, blank=True, default="")
    address = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Profile"
        verbose_name_plural = "Customer Profiles"

    def __str__(self):
        return f"Profile: {self.user.username} ({self.phone or 'No phone'})"


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.get_or_create(user=instance)


class Location(models.Model):
    name = models.CharField(max_length=150, help_text="Location / Terminal Name")
    address = models.CharField(max_length=255, help_text="Detailed address / Pickup point")
    maps_link = models.URLField(blank=True, default="", help_text="Google Maps URL")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Pickup Location"
        verbose_name_plural = "Pickup Locations"

    def __str__(self):
        return self.name


class Car(models.Model):
    VEHICLE_CLASS_CHOICES = [
        ('SUV', 'SUV / Compact SUV'),
        ('Hatchback', 'Hatchback'),
        ('Sedan', 'Sedan'),
        ('MUV', 'MUV / 7-Seater'),
        ('Luxury', 'Luxury'),
    ]

    FUEL_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('EV', 'Electric Vehicle (EV)'),
        ('CNG', 'CNG'),
    ]

    TRANSMISSION_CHOICES = [
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
    ]

    brand = models.CharField(max_length=60)
    model = models.CharField(max_length=80)
    vehicle_class = models.CharField(max_length=30, choices=VEHICLE_CLASS_CHOICES, default='SUV')
    price_per_day = models.PositiveIntegerField(help_text="Daily rental rate in ₹ (INR)")
    security_deposit = models.PositiveIntegerField(default=3000, help_text="Refundable deposit in ₹ (INR)")
    seats = models.PositiveSmallIntegerField(default=5)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='Petrol')
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='Manual')
    ac_status = models.CharField(max_length=40, default="Cold A/C")
    included_km = models.PositiveIntegerField(default=250, help_text="Free KM per day")
    extra_km_rate = models.PositiveSmallIntegerField(default=12, help_text="Extra charge per KM beyond limit")
    badge = models.CharField(max_length=40, blank=True, default="", help_text="e.g. Popular, Economic, 7-Seater")
    image_url = models.URLField(max_length=500, default="", help_text="Direct image URL")
    description = models.TextField(blank=True, default="")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', 'price_per_day']
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.vehicle_class})"

    @property
    def display_title(self):
        return f"{self.brand} {self.model}"

    def is_available_for_dates(self, pickup_date, return_date, exclude_booking_id=None):
        """Check if vehicle has any overlapping confirmed or pending bookings for given date range."""
        if not pickup_date or not return_date:
            return True
        bookings = BookingRequest.objects.filter(
            car=self,
            status__in=['PENDING', 'CONFIRMED'],
            pickup_date__lte=return_date,
            return_date__gte=pickup_date
        )
        if exclude_booking_id:
            bookings = bookings.exclude(id=exclude_booking_id)
        return not bookings.exists()


def generate_booking_ref():
    random_part = uuid.uuid4().hex[:4].upper()
    year = timezone.now().year
    return f"KTF-{year}-{random_part}"


class BookingRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Owner Confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('REJECTED', 'Unavailable / Rejected'),
        ('CANCELLED', 'Cancelled by Customer'),
        ('COMPLETED', 'Completed'),
    ]

    WHATSAPP_STATUS_CHOICES = [
        ('NOT_SENT', 'Not Sent'),
        ('SENT', 'Sent to Customer'),
        ('FAILED', 'Delivery Failed'),
    ]

    EMAIL_STATUS_CHOICES = [
        ('NOT_SENT', 'Not Sent'),
        ('SENT', 'Sent to Customer'),
        ('FAILED', 'Delivery Failed'),
    ]

    booking_ref = models.CharField(
        max_length=30,
        unique=True,
        default=generate_booking_ref,
        editable=False,
        help_text="Unique booking reference code"
    )
    # Optional foreign key (not required for guest checkout)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        help_text="Staff or registered user (optional)"
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings')

    # Guest details stored directly
    customer_name = models.CharField(max_length=120, help_text="Guest full name")
    customer_phone = models.CharField(max_length=20, db_index=True, blank=True, default="", help_text="Guest phone / mobile number")
    customer_mobile = models.CharField(max_length=20, blank=True, default="", help_text="Alternate mobile number")
    customer_whatsapp = models.CharField(max_length=20, blank=True, default="", help_text="WhatsApp contact number")
    customer_email = models.EmailField(blank=True, default="", help_text="Guest email address")
    driving_license_number = models.CharField(max_length=50, blank=True, default="", help_text="Guest Driving License ID")

    pickup_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pickup_bookings'
    )
    pickup_date = models.DateField(default=date.today)
    pickup_time = models.CharField(max_length=10, default="10:00")
    return_date = models.DateField(default=date.today)
    return_time = models.CharField(max_length=10, default="10:00")
    total_days = models.PositiveSmallIntegerField(default=1)
    
    # Financial breakdowns (Offline payment upon pickup)
    estimated_amount = models.PositiveIntegerField(default=0, help_text="Gross rental amount before discount")
    discount_amount = models.PositiveIntegerField(default=0, help_text="Multi-day / promotional discount")
    net_rental_amount = models.PositiveIntegerField(default=0, help_text="Net rental fee payable")
    security_deposit = models.PositiveIntegerField(default=3000, help_text="Refundable deposit")
    payable_at_pickup = models.PositiveIntegerField(default=0, help_text="Total cash/UPI due on vehicle pickup")
    
    payment_mode = models.CharField(
        max_length=40,
        default="OFFLINE_AT_PICKUP",
        help_text="Offline Cash / UPI upon vehicle inspection"
    )

    policy_accepted = models.BooleanField(
        default=True,
        help_text="Customer accepted Vehicle Care & Damage Policy"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    whatsapp_status = models.CharField(
        max_length=20,
        choices=WHATSAPP_STATUS_CHOICES,
        default='NOT_SENT'
    )
    email_status = models.CharField(
        max_length=20,
        choices=EMAIL_STATUS_CHOICES,
        default='NOT_SENT'
    )
    cancellation_reason = models.TextField(blank=True, default="")
    owner_notes = models.TextField(blank=True, default="", help_text="Internal owner notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Booking Request"
        verbose_name_plural = "Booking Requests"

    def __str__(self):
        return f"{self.booking_ref} - {self.customer_name} ({self.car})"

    @property
    def booking_reference(self):
        return self.booking_ref

    @property
    def start_date(self):
        return self.pickup_date

    @property
    def end_date(self):
        return self.return_date

    @property
    def total_amount(self):
        return self.payable_at_pickup or self.net_rental_amount

    @property
    def total_free_km(self):
        if self.car:
            return self.total_days * self.car.included_km
        return 0

    def calculate_pricing(self):
        """Calculate duration, discounts, net amount, and payable offline amount."""
        if self.pickup_date and self.return_date:
            delta = (self.return_date - self.pickup_date).days
            self.total_days = max(1, delta if delta > 0 else 1)
        else:
            self.total_days = 1

        if self.car:
            base_total = self.total_days * self.car.price_per_day
            self.estimated_amount = base_total
            self.security_deposit = self.car.security_deposit
            
            # Duration discounts: 7+ days = 10% off, 14+ days = 15% off
            if self.total_days >= 14:
                self.discount_amount = int(base_total * 0.15)
            elif self.total_days >= 7:
                self.discount_amount = int(base_total * 0.10)
            else:
                self.discount_amount = 0

            self.net_rental_amount = max(0, self.estimated_amount - self.discount_amount)
            self.payable_at_pickup = self.net_rental_amount + self.security_deposit

    def save(self, *args, **kwargs):
        if not self.booking_ref:
            self.booking_ref = generate_booking_ref()
        # Ensure customer_phone / mobile / whatsapp sync
        if not self.customer_phone and self.customer_mobile:
            self.customer_phone = self.customer_mobile
        elif not self.customer_mobile and self.customer_phone:
            self.customer_mobile = self.customer_phone
        if not self.customer_whatsapp and self.customer_phone:
            self.customer_whatsapp = self.customer_phone

        self.calculate_pricing()
        super().save(*args, **kwargs)


# Alias Booking to BookingRequest for clean and flexible imports
Booking = BookingRequest
