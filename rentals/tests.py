from django.test import TestCase, Client
from django.urls import reverse

class Part1FrontendAndBrandingTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_loads_and_has_branding(self):
        """Test homepage renders with status 200, dark theme tokens, and brand name."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Keys to your freedom")
        self.assertContains(response, "theme.css")
        self.assertContains(response, "mobile-bottom-nav")
        self.assertContains(response, "Featured Fleet")

    def test_cars_list_page_loads_and_filters(self):
        """Test fleet listing page renders properly and handles filters."""
        response = self.client.get(reverse('cars_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Available Self-Drive Vehicles")
        self.assertContains(response, "Creta")
        self.assertContains(response, "Swift")
        
        # Test class filter
        filter_response = self.client.get(reverse('cars_list') + '?vehicle_class=SUV')
        self.assertEqual(filter_response.status_code, 200)
        self.assertContains(filter_response, "Creta")
        self.assertNotContains(filter_response, "Swift")

    def test_car_detail_page_loads(self):
        """Test car detail page renders specifications and booking CTA."""
        response = self.client.get(reverse('car_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hyundai")
        self.assertContains(response, "Creta")
        self.assertContains(response, "Key Specifications")
        self.assertContains(response, "Booking Request System")

    def test_booking_form_has_whatsapp_and_policy_elements(self):
        """Test booking request form contains customer WhatsApp field & policy card."""
        response = self.client.get(reverse('booking_form', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "WhatsApp Number")
        self.assertContains(response, "Same as mobile number")
        self.assertContains(response, "Vehicle Care & Damage Policy")
        self.assertContains(response, "policy_accepted")
        self.assertContains(response, "Submit Booking Request")
        self.assertContains(response, "NOT confirmed yet")


    def test_booking_submission_flow(self):
        """Test submitting booking displays pending confirmation with warning."""
        payload = {
            'car_id': 1,
            'customer_name': 'Rahul Sharma',
            'customer_mobile': '+919876543210',
            'customer_whatsapp': '+919876543210',
            'pickup_location': '1',
            'pickup_date': '2026-10-05',
            'pickup_time': '10:00',
            'return_date': '2026-10-08',
            'return_time': '10:00',
            'policy_accepted': 'on',
        }
        response = self.client.post(reverse('booking_submit'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BOOKING REQUEST RECEIVED")
        self.assertContains(response, "YOUR BOOKING IS NOT CONFIRMED YET")
        self.assertContains(response, "PENDING")
        self.assertContains(response, "WhatsApp Owner")
        self.assertContains(response, "Call Owner")
        self.assertContains(response, "KTF-2026-0001")

    def test_policy_and_rules_pages(self):
        """Test rental policy, rules, contact, about, and privacy pages."""
        pages = ['rental_policy', 'rental_rules', 'contact', 'about', 'privacy', 'admin_shell_preview']
        for page_name in pages:
            response = self.client.get(reverse(page_name))
            self.assertEqual(response.status_code, 200, f"Page {page_name} failed to load.")
            self.assertContains(response, "Keys to your freedom")
