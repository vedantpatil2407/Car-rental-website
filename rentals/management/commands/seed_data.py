from django.core.management.base import BaseCommand
from datetime import date, timedelta
from rentals.models import Location, Car, BookingRequest


class Command(BaseCommand):
    help = "Seed database with initial locations, vehicles fleet, and sample booking requests"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # 1. Locations
        locations_data = [
            {
                'name': 'Dabolim International Airport Terminal',
                'address': 'Arrival Pick-up Zone 2, Dabolim, Goa',
                'maps_link': 'https://maps.google.com/?q=Goa+Airport',
            },
            {
                'name': 'Mopa (Manohar) International Airport',
                'address': 'Commercial Hub Exit, Pernem, North Goa',
                'maps_link': 'https://maps.google.com/?q=Mopa+Airport',
            },
            {
                'name': 'Central City Hub & Train Junction',
                'address': 'Station Road, Near Bus Interchange',
                'maps_link': 'https://maps.google.com/?q=Madgaon+Railway+Station',
            },
            {
                'name': 'Candolim / Calangute Beach Hub',
                'address': 'Main Road Hub, Near Fort Aguada Road, North Goa',
                'maps_link': 'https://maps.google.com/?q=Candolim+Goa',
            }
        ]

        created_locations = []
        for loc in locations_data:
            obj, created = Location.objects.get_or_create(
                name=loc['name'],
                defaults={'address': loc['address'], 'maps_link': loc['maps_link']}
            )
            created_locations.append(obj)
            if created:
                self.stdout.write(f"  + Created Location: {obj.name}")

        # 2. Cars
        cars_data = [
            {
                'brand': 'Hyundai',
                'model': 'Creta SX (O)',
                'vehicle_class': 'SUV',
                'price_per_day': 2800,
                'security_deposit': 3000,
                'seats': 5,
                'fuel_type': 'Diesel',
                'transmission': 'Manual',
                'ac_status': 'Cold A/C',
                'included_km': 250,
                'badge': 'Popular',
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=800&q=80',
                'description': 'Spacious and commanding compact SUV, ideal for city cruising and long highway drives with high fuel economy.',
            },
            {
                'brand': 'Maruti Suzuki',
                'model': 'Swift ZXi',
                'vehicle_class': 'Hatchback',
                'price_per_day': 1600,
                'security_deposit': 2500,
                'seats': 5,
                'fuel_type': 'Petrol',
                'transmission': 'Manual',
                'ac_status': 'Cold A/C',
                'included_km': 200,
                'badge': 'Economic',
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1590362891991-f776e747a588?auto=format&fit=crop&w=800&q=80',
                'description': 'Agile, reliable, and fuel-efficient hatchback designed for easy urban navigation and effortless parking.',
            },
            {
                'brand': 'Mahindra',
                'model': 'Thar 4x4 Hard Top',
                'vehicle_class': 'SUV',
                'price_per_day': 3500,
                'security_deposit': 5000,
                'seats': 4,
                'fuel_type': 'Diesel',
                'transmission': 'Automatic',
                'ac_status': 'Cold A/C',
                'included_km': 200,
                'badge': 'Adventure',
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=800&q=80',
                'description': 'Iconic 4x4 off-road SUV with high ground clearance, powerful torque, and commanding road presence.',
            },
            {
                'brand': 'Toyota',
                'model': 'Innova Crysta',
                'vehicle_class': 'MUV',
                'price_per_day': 4200,
                'security_deposit': 5000,
                'seats': 7,
                'fuel_type': 'Diesel',
                'transmission': 'Automatic',
                'ac_status': 'Dual A/C',
                'included_km': 300,
                'badge': '7-Seater',
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=800&q=80',
                'description': 'Ultimate comfort for family vacations and group travels with captain seating and large luggage volume.',
            },
            {
                'brand': 'Honda',
                'model': 'City V-CVT',
                'vehicle_class': 'Sedan',
                'price_per_day': 2400,
                'security_deposit': 3000,
                'seats': 5,
                'fuel_type': 'Petrol',
                'transmission': 'Automatic',
                'ac_status': 'Cold A/C',
                'included_km': 250,
                'badge': 'Comfort Sedan',
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=800&q=80',
                'description': 'Smooth luxury sedan with premium ride quality, plush interior finish, and effortless automatic gearbox.',
            },
            {
                'brand': 'Tata',
                'model': 'Nexon EV Prime',
                'vehicle_class': 'SUV',
                'price_per_day': 2600,
                'security_deposit': 4000,
                'seats': 5,
                'fuel_type': 'EV',
                'transmission': 'Automatic',
                'ac_status': 'Climate Control',
                'included_km': 220,
                'badge': 'Eco Electric',
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=800&q=80',
                'description': 'Modern zero-emission electric compact SUV with instant acceleration and whisper-quiet cabin comfort.',
            },
            {
                'brand': 'Kia',
                'model': 'Seltos GTX Plus',
                'vehicle_class': 'SUV',
                'price_per_day': 3000,
                'security_deposit': 3500,
                'seats': 5,
                'fuel_type': 'Petrol',
                'transmission': 'Automatic',
                'ac_status': 'Ventilated Seats',
                'included_km': 250,
                'badge': 'Tech Loaded',
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=800&q=80',
                'description': 'Feature-packed compact crossover with sunroof, Bose premium sound, and 360-degree camera assist.',
            }
        ]

        created_cars = []
        for cdata in cars_data:
            car, created = Car.objects.get_or_create(
                brand=cdata['brand'],
                model=cdata['model'],
                defaults=cdata
            )
            created_cars.append(car)
            if created:
                self.stdout.write(f"  + Created Car: {car}")

        # 3. Sample Booking Requests
        if created_cars and created_locations:
            sample_bookings = [
                {
                    'car': created_cars[0],
                    'customer_name': 'Amit Verma',
                    'customer_mobile': '+919822114455',
                    'customer_whatsapp': '+919822114455',
                    'pickup_location': created_locations[0],
                    'pickup_date': date.today() + timedelta(days=2),
                    'pickup_time': '11:00',
                    'return_date': date.today() + timedelta(days=5),
                    'return_time': '18:00',
                    'status': 'PENDING',
                    'whatsapp_status': 'NOT_SENT',
                    'policy_accepted': True,
                    'owner_notes': 'Customer requested airport pickup directly at Terminal arrival gate.',
                },
                {
                    'car': created_cars[2],
                    'customer_name': 'Rohit Kulkarni',
                    'customer_mobile': '+919988776655',
                    'customer_whatsapp': '+919988776655',
                    'pickup_location': created_locations[1],
                    'pickup_date': date.today() + timedelta(days=1),
                    'pickup_time': '09:00',
                    'return_date': date.today() + timedelta(days=4),
                    'return_time': '20:00',
                    'status': 'CONFIRMED',
                    'whatsapp_status': 'SENT',
                    'policy_accepted': True,
                    'owner_notes': 'Verified driving license and confirmed via WhatsApp.',
                },
                {
                    'car': created_cars[1],
                    'customer_name': 'Priya Deshmukh',
                    'customer_mobile': '+919766554433',
                    'customer_whatsapp': '+919766554433',
                    'pickup_location': created_locations[2],
                    'pickup_date': date.today() + timedelta(days=4),
                    'pickup_time': '14:00',
                    'return_date': date.today() + timedelta(days=6),
                    'return_time': '12:00',
                    'status': 'PENDING',
                    'whatsapp_status': 'NOT_SENT',
                    'policy_accepted': True,
                    'owner_notes': 'Awaiting advance confirmation message.',
                }
            ]

            for sbook in sample_bookings:
                if not BookingRequest.objects.filter(customer_mobile=sbook['customer_mobile']).exists():
                    b = BookingRequest.objects.create(**sbook)
                    self.stdout.write(f"  + Created Booking Request: {b.booking_ref} ({b.customer_name})")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
