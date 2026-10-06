from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, timedelta
from rentals.models import Location, Car, BookingRequest, Booking
from rentals.services import NotificationService


class Part1FrontendAndBrandingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.location = Location.objects.create(
            name="Dabolim International Airport Terminal",
            address="Arrival Pick-up Zone 2, Dabolim, Goa",
            maps_link="https://maps.google.com/?q=Goa+Airport"
        )
        self.car = Car.objects.create(
            brand="Hyundai",
            model="Creta SX (O)",
            vehicle_class="SUV",
            price_per_day=2800,
            security_deposit=3000,
            seats=5,
            fuel_type="Diesel",
            transmission="Manual",
            ac_status="Cold A/C",
            included_km=250,
            badge="Popular",
            is_featured=True,
            image_url="https://images.unsplash.com/photo-1549399542-7e3f8b79c341",
            description="Spacious compact SUV"
        )

    def test_homepage_loads_and_has_branding(self):
        """Test homepage renders with status 200, dark theme tokens, brand name, and Track Booking link."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Keys to your freedom")
        self.assertContains(response, "theme.css")
        self.assertContains(response, "mobile-bottom-nav")
        self.assertContains(response, "Featured Fleet")
        self.assertContains(response, "Track Booking")

    def test_policy_and_rules_pages(self):
        """Test rental policy, rules, contact, about, and privacy pages."""
        pages = ['rental_policy', 'rental_rules', 'contact', 'about', 'privacy', 'admin_shell_preview', 'booking_lookup']
        for page_name in pages:
            response = self.client.get(reverse(page_name))
            self.assertEqual(response.status_code, 200, f"Page {page_name} failed to load.")
            self.assertContains(response, "Keys to your freedom")


class GuestCheckoutAndBookingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.location = Location.objects.create(name="Panaji Central Hub", address="Patto Plaza, Panaji")
        self.car = Car.objects.create(
            brand="Tata",
            model="Harrier XZA",
            vehicle_class="SUV",
            price_per_day=3200,
            security_deposit=4000,
            included_km=250
        )

    def test_guest_booking_submission_direct(self):
        """Test guest can submit a booking without any account or authentication."""
        post_data = {
            'car_id': self.car.id,
            'customer_name': 'Amit Patel',
            'customer_phone': '+91 9988776655',
            'customer_email': 'amit@example.com',
            'driving_license_number': 'DL-04-2023-9988',
            'pickup_location': self.location.id,
            'pickup_date': (date.today() + timedelta(days=2)).isoformat(),
            'pickup_time': '11:00',
            'return_date': (date.today() + timedelta(days=5)).isoformat(),
            'return_time': '18:00',
            'policy_accepted': 'on'
        }
        response = self.client.post(reverse('booking_submit'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BOOKING REQUEST RECEIVED")
        self.assertContains(response, "Amit Patel")
        self.assertContains(response, "Harrier XZA")
        self.assertContains(response, "NO ONLINE PAYMENT REQUIRED")

        # Verify DB storage directly on Booking model
        booking = BookingRequest.objects.get(customer_email='amit@example.com')
        self.assertIsNone(booking.user)
        self.assertEqual(booking.customer_name, 'Amit Patel')
        self.assertEqual(booking.customer_phone, '+91 9988776655')
        self.assertEqual(booking.driving_license_number, 'DL-04-2023-9988')
        self.assertTrue(booking.booking_ref.startswith("KTF-"))
        self.assertEqual(booking.total_days, 3)
        self.assertEqual(booking.estimated_amount, 3 * 3200)
        self.assertEqual(booking.payable_at_pickup, (3 * 3200) + 4000)

    def test_digital_rental_voucher_view(self):
        """Test digital voucher renders complete offline breakdown and vehicle specs."""
        booking = BookingRequest.objects.create(
            car=self.car,
            customer_name="Rohan Verma",
            customer_phone="+91 9876543210",
            customer_email="customer@example.com",
            driving_license_number="DL-GOA-2024-11",
            pickup_location=self.location,
            pickup_date=date.today() + timedelta(days=2),
            return_date=date.today() + timedelta(days=5),
            status='CONFIRMED'
        )

        resp = self.client.get(reverse('booking_voucher', args=[booking.booking_ref]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, booking.booking_ref)
        self.assertContains(resp, "CONFIRMED")
        self.assertContains(resp, "Offline Payment Breakdown")
        self.assertContains(resp, "Rohan Verma")
        self.assertContains(resp, "DL-GOA-2024-11")

    def test_guest_booking_lookup_by_ref_and_phone(self):
        """Test guest customer looking up reservation by booking ref and mobile."""
        booking = BookingRequest.objects.create(
            car=self.car,
            customer_name="Guest Renter",
            customer_phone="9871122334",
            customer_mobile="9871122334",
            pickup_location=self.location,
            pickup_date=date.today() + timedelta(days=3),
            return_date=date.today() + timedelta(days=4),
            status='PENDING'
        )

        resp = self.client.post(reverse('booking_lookup'), {
            'booking_reference': booking.booking_ref,
            'customer_phone': '9871122334'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, booking.booking_ref)
        self.assertContains(resp, "Guest Renter")

    def test_guest_booking_cancellation(self):
        """Test guest can cancel a pending booking from voucher or portal."""
        booking = BookingRequest.objects.create(
            car=self.car,
            customer_name="Rohan Verma",
            customer_phone="+91 9876543210",
            customer_email="customer@example.com",
            status='PENDING'
        )

        cancel_resp = self.client.post(reverse('cancel_booking', args=[booking.booking_ref]), {
            'reason': 'Trip rescheduled'
        })
        self.assertEqual(cancel_resp.status_code, 302)

        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CANCELLED')


class PricingAndAvailabilityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.car = Car.objects.create(
            brand="Mahindra",
            model="Thar 4x4",
            vehicle_class="SUV",
            price_per_day=3000,
            security_deposit=5000,
            included_km=250
        )
        self.location = Location.objects.create(name="Airport Hub", address="Terminal 1")

    def test_multi_day_discount_and_offline_payment_calculation(self):
        """Test automatic multi-day discount calculation (10% for 7+ days, 15% for 14+ days)."""
        # 1-day booking: 1 * 3000 = 3000, 0 disc, payable = 3000 + 5000 = 8000
        b1 = BookingRequest.objects.create(
            car=self.car,
            customer_name="Short Trip",
            customer_phone="9900112233",
            pickup_date=date(2026, 11, 1),
            return_date=date(2026, 11, 2)
        )
        self.assertEqual(b1.total_days, 1)
        self.assertEqual(b1.estimated_amount, 3000)
        self.assertEqual(b1.discount_amount, 0)
        self.assertEqual(b1.net_rental_amount, 3000)
        self.assertEqual(b1.payable_at_pickup, 8000)
        self.assertEqual(b1.total_free_km, 250)
        self.assertEqual(b1.booking_reference, b1.booking_ref)
        self.assertEqual(b1.start_date, b1.pickup_date)
        self.assertEqual(b1.end_date, b1.return_date)

        # 7-day booking: 7 * 3000 = 21,000, 10% disc = 2100, net = 18,900, payable = 18900 + 5000 = 23,900
        b7 = BookingRequest.objects.create(
            car=self.car,
            customer_name="Weekly Trip",
            customer_phone="9900112233",
            pickup_date=date(2026, 11, 1),
            return_date=date(2026, 11, 8)
        )
        self.assertEqual(b7.total_days, 7)
        self.assertEqual(b7.estimated_amount, 21000)
        self.assertEqual(b7.discount_amount, 2100)
        self.assertEqual(b7.net_rental_amount, 18900)
        self.assertEqual(b7.payable_at_pickup, 23900)
        self.assertEqual(b7.total_free_km, 1750)

    def test_overlap_availability_check(self):
        """Test calendar engine blocks conflicting booking on overlapping dates."""
        BookingRequest.objects.create(
            car=self.car,
            customer_name="Existing Renter",
            customer_phone="9988776655",
            pickup_date=date(2026, 12, 10),
            return_date=date(2026, 12, 15),
            status='CONFIRMED'
        )

        # Check availability methods
        self.assertFalse(self.car.is_available_for_dates(date(2026, 12, 12), date(2026, 12, 14)))
        self.assertFalse(self.car.is_available_for_dates(date(2026, 12, 8), date(2026, 12, 11)))
        self.assertTrue(self.car.is_available_for_dates(date(2026, 12, 16), date(2026, 12, 20)))


class NotificationServicesTests(TestCase):
    def setUp(self):
        self.car = Car.objects.create(
            brand="Honda",
            model="City ZX",
            vehicle_class="Sedan",
            price_per_day=2200,
            security_deposit=3000
        )
        self.booking = BookingRequest.objects.create(
            car=self.car,
            customer_name="Ananya Sen",
            customer_phone="9823456789",
            customer_email="ananya@example.com",
            pickup_date=date(2026, 10, 20),
            return_date=date(2026, 10, 22),
            status='PENDING'
        )

    def test_whatsapp_message_and_link_generation(self):
        """Test rich WhatsApp message generation with reference ID and offline payment."""
        wa_text = NotificationService.generate_whatsapp_text(self.booking, 'CONFIRMED')
        self.assertIn("BOOKING CONFIRMED", wa_text)
        self.assertIn(self.booking.booking_ref, wa_text)
        self.assertIn("Honda City ZX", wa_text)
        self.assertIn("Offline Payment Summary", wa_text)
        self.assertIn("UPI or Cash", wa_text)

        wa_link = NotificationService.get_whatsapp_deep_link(self.booking, 'CONFIRMED')
        self.assertTrue(wa_link.startswith("https://wa.me/9823456789?text="))

    def test_automated_notification_dispatch(self):
        """Test notification service triggers email and updates status."""
        results = NotificationService.send_automated_notifications(self.booking, 'CONFIRMED')
        self.assertTrue(results['email_sent'])
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.email_status, 'SENT')
