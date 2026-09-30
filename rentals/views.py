from django.shortcuts import render, redirect
from datetime import date, timedelta

# Initial mock fleet catalogue for Part 1 UI presentation (to be replaced with database models in Part 2)
MOCK_CARS = [
    {
        'id': 1,
        'brand': 'Hyundai',
        'model': 'Creta SX (O)',
        'vehicle_class': 'SUV',
        'price_per_day': 2800,
        'seats': 5,
        'fuel_type': 'Diesel',
        'transmission': 'Manual',
        'ac_status': 'Cold A/C',
        'included_km': 250,
        'badge': 'Popular',
        'image_url': 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=800&q=80',
        'description': 'Spacious and commanding compact SUV, ideal for city cruising and long highway drives with high fuel economy.',
    },
    {
        'id': 2,
        'brand': 'Maruti Suzuki',
        'model': 'Swift ZXi',
        'vehicle_class': 'Hatchback',
        'price_per_day': 1600,
        'seats': 5,
        'fuel_type': 'Petrol',
        'transmission': 'Manual',
        'ac_status': 'Cold A/C',
        'included_km': 200,
        'badge': 'Economic',
        'image_url': 'https://images.unsplash.com/photo-1590362891991-f776e747a588?auto=format&fit=crop&w=800&q=80',
        'description': 'Agile, reliable, and fuel-efficient hatchback designed for easy urban navigation and effortless parking.',
    },
    {
        'id': 3,
        'brand': 'Mahindra',
        'model': 'Thar 4x4 Hard Top',
        'vehicle_class': 'SUV',
        'price_per_day': 3500,
        'seats': 4,
        'fuel_type': 'Diesel',
        'transmission': 'Automatic',
        'ac_status': 'Cold A/C',
        'included_km': 200,
        'badge': 'Adventure',
        'image_url': 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=800&q=80',
        'description': 'Iconic 4x4 off-road SUV with high ground clearance, powerful torque, and commanding road presence.',
    },
    {
        'id': 4,
        'brand': 'Toyota',
        'model': 'Innova Crysta',
        'vehicle_class': 'MUV',
        'price_per_day': 4200,
        'seats': 7,
        'fuel_type': 'Diesel',
        'transmission': 'Automatic',
        'ac_status': 'Dual A/C',
        'included_km': 300,
        'badge': '7-Seater',
        'image_url': 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=800&q=80',
        'description': 'Ultimate comfort for family vacations and group travels with captain seating and large luggage volume.',
    },
    {
        'id': 5,
        'brand': 'Honda',
        'model': 'City V-CVT',
        'vehicle_class': 'Sedan',
        'price_per_day': 2400,
        'seats': 5,
        'fuel_type': 'Petrol',
        'transmission': 'Automatic',
        'ac_status': 'Cold A/C',
        'included_km': 250,
        'badge': 'Comfort Sedan',
        'image_url': 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=800&q=80',
        'description': 'Smooth luxury sedan with premium ride quality, plush interior finish, and effortless automatic gearbox.',
    },
    {
        'id': 6,
        'brand': 'Tata',
        'model': 'Nexon EV Prime',
        'vehicle_class': 'SUV',
        'price_per_day': 2600,
        'seats': 5,
        'fuel_type': 'EV',
        'transmission': 'Automatic',
        'ac_status': 'Climate Control',
        'included_km': 220,
        'badge': 'Eco Electric',
        'image_url': 'https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=800&q=80',
        'description': 'Modern zero-emission electric compact SUV with instant acceleration and whisper-quiet cabin comfort.',
    },
]

MOCK_LOCATIONS = [
    {
        'id': 1,
        'name': 'Dabolim International Airport Terminal',
        'address': 'Arrival Pick-up Zone 2, Dabolim, Goa',
        'maps_link': 'https://maps.google.com/?q=Goa+Airport',
    },
    {
        'id': 2,
        'name': 'Mopa (Manohar) International Airport',
        'address': 'Commercial Hub Exit, Pernem, North Goa',
        'maps_link': 'https://maps.google.com/?q=Mopa+Airport',
    },
    {
        'id': 3,
        'name': 'Central City Hub & Train Junction',
        'address': 'Station Road, Near Bus Interchange',
        'maps_link': 'https://maps.google.com/?q=Madgaon+Railway+Station',
    },
]


def home_view(request):
    """Render public homepage with search widget and featured cars."""
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=2)).isoformat()
    return render(request, 'rentals/home.html', {
        'featured_cars': MOCK_CARS[:3],
        'locations': MOCK_LOCATIONS,
        'today': today,
        'tomorrow': tomorrow,
    })


def cars_list_view(request):
    """Render fleet catalog with filter parameters."""
    selected_class = request.GET.get('vehicle_class', '')
    selected_trans = request.GET.get('transmission', '')
    selected_fuel = request.GET.get('fuel_type', '')

    filtered = MOCK_CARS
    if selected_class:
        filtered = [c for c in filtered if c['vehicle_class'].lower() == selected_class.lower()]
    if selected_trans:
        filtered = [c for c in filtered if selected_trans.lower() in c['transmission'].lower()]
    if selected_fuel:
        filtered = [c for c in filtered if c['fuel_type'].lower() == selected_fuel.lower()]

    return render(request, 'rentals/cars.html', {
        'cars': filtered,
        'locations': MOCK_LOCATIONS,
        'selected_class': selected_class,
        'selected_trans': selected_trans,
        'selected_fuel': selected_fuel,
    })


def car_detail_view(request, car_id):
    """Render car specification and rental detail view."""
    car = next((c for c in MOCK_CARS if c['id'] == int(car_id)), MOCK_CARS[0])
    return render(request, 'rentals/car_detail.html', {
        'car': car,
        'locations': MOCK_LOCATIONS,
    })


def booking_form_view(request, car_id):
    """Render booking request form with mandatory policy acceptance and WhatsApp number field."""
    car = next((c for c in MOCK_CARS if c['id'] == int(car_id)), MOCK_CARS[0])
    return render(request, 'rentals/booking_form.html', {
        'car': car,
        'locations': MOCK_LOCATIONS,
    })


def booking_submit_view(request):
    """Handle booking submission and show booking submitted confirmation page."""
    if request.method == 'POST':
        car_id = request.POST.get('car_id', 1)
        car = next((c for c in MOCK_CARS if c['id'] == int(car_id)), MOCK_CARS[0])
        customer_name = request.POST.get('customer_name', 'Customer')
        customer_mobile = request.POST.get('customer_mobile', '')
        customer_whatsapp = request.POST.get('customer_whatsapp', customer_mobile)
        pickup_location_id = request.POST.get('pickup_location', '')
        pickup_date = request.POST.get('pickup_date', '')
        pickup_time = request.POST.get('pickup_time', '10:00')
        return_date = request.POST.get('return_date', '')
        return_time = request.POST.get('return_time', '10:00')
        
        loc_name = 'Main Terminal'
        for loc in MOCK_LOCATIONS:
            if str(loc['id']) == str(pickup_location_id):
                loc_name = loc['name']

        # Generate sample human-friendly reference for Part 1 UI demonstration
        booking_ref = "KTF-2026-0001"

        return render(request, 'rentals/booking_submitted.html', {
            'car': car,
            'booking_ref': booking_ref,
            'customer_name': customer_name,
            'customer_whatsapp': customer_whatsapp,
            'pickup_location': loc_name,
            'pickup_date': pickup_date,
            'pickup_time': pickup_time,
            'return_date': return_date,
            'return_time': return_time,
        })
    return redirect('cars_list')


def contact_view(request):
    """Render contact and pickup location information."""
    return render(request, 'rentals/contact.html', {
        'locations': MOCK_LOCATIONS,
    })


def about_view(request):
    """Render about page."""
    return render(request, 'rentals/about.html')


def rental_policy_view(request):
    """Render dedicated Vehicle Care & Damage Policy page."""
    return render(request, 'rentals/rental_policy.html')


def rental_rules_view(request):
    """Render practical rental rules and guidelines."""
    return render(request, 'rentals/rental_rules.html')


def privacy_view(request):
    """Render privacy policy and data security details."""
    return render(request, 'rentals/privacy.html')


def admin_shell_preview_view(request):
    """Render Owner Admin Portal preview shell."""
    return render(request, 'rentals/admin_shell.html')
