from django import forms
from .models import BookingRequest, Location, Car, CustomerProfile


class BookingForm(forms.ModelForm):
    """Guest checkout booking form requiring no user registration."""
    customer_name = forms.CharField(
        max_length=120,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Rahul Sharma', 'id': 'customerName'})
    )
    customer_phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. +91 98765 43210', 'id': 'customerPhone'})
    )
    customer_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'e.g. rahul@example.com', 'id': 'customerEmail'})
    )
    driving_license_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. DL-0420210012345', 'id': 'drivingLicense'})
    )
    pickup_location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True),
        required=True,
        empty_label="Select Pickup Point",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'pickupLocation'})
    )
    pickup_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input', 'id': 'pickupDate'})
    )
    pickup_time = forms.CharField(
        max_length=10,
        required=False,
        initial="10:00",
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input', 'id': 'pickupTime'})
    )
    return_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input', 'id': 'returnDate'})
    )
    return_time = forms.CharField(
        max_length=10,
        required=False,
        initial="10:00",
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input', 'id': 'returnTime'})
    )
    policy_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox', 'id': 'policyAcceptance'})
    )

    class Meta:
        model = BookingRequest
        fields = [
            'customer_name', 'customer_phone', 'customer_email',
            'driving_license_number', 'pickup_location',
            'pickup_date', 'pickup_time', 'return_date', 'return_time',
            'policy_accepted'
        ]

    def clean(self):
        cleaned_data = super().clean()
        p_date = cleaned_data.get('pickup_date')
        r_date = cleaned_data.get('return_date')
        if p_date and r_date and r_date < p_date:
            self.add_error('return_date', "Return date cannot be earlier than pickup date.")
        return cleaned_data


class BookingLookupForm(forms.Form):
    """Guest booking status lookup form using reference code & phone number."""
    booking_reference = forms.CharField(
        max_length=35,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. KTF-2026-ABCD',
            'id': 'bookingRefInput'
        })
    )
    customer_phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Registered mobile / WhatsApp number',
            'id': 'customerPhoneInput'
        })
    )


class CarReviewForm(forms.Form):
    """Review & rating submission form using Customer Name and Booking Reference ID."""
    customer_name = forms.CharField(
        max_length=120,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Your Full Name (e.g. Rahul Sharma)',
            'id': 'reviewCustomerName'
        })
    )
    booking_reference = forms.CharField(
        max_length=35,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. KTF-2026-ABCD (for Verified Renter badge)',
            'id': 'reviewBookingRef'
        })
    )
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=5,
        required=True,
        widget=forms.HiddenInput(attrs={'id': 'selectedRatingInput'})
    )
    trip_type = forms.ChoiceField(
        choices=[
            ('Vacation', '🏖️ Vacation / Holiday'),
            ('Family', '👨‍👩‍👦 Family Trip'),
            ('RoadTrip', '🛣️ Road Trip / Weekend Drive'),
            ('Business', '💼 Business / Work'),
            ('Local', '🚗 Local City Drive'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'reviewTripType'})
    )
    title = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Short headline (e.g. Pristine car condition, super smooth drive!)',
            'id': 'reviewTitle'
        })
    )
    comment = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 4,
            'placeholder': 'Share your experience with the car, pickup process, fuel efficiency, cleanliness, etc.',
            'id': 'reviewComment'
        })
    )


class CarForm(forms.ModelForm):
    """Admin & Owner portal form for creating and updating vehicles in the fleet."""
    class Meta:
        model = Car
        fields = [
            'brand', 'model', 'vehicle_class', 'badge',
            'price_per_day', 'security_deposit', 'included_km', 'extra_km_rate',
            'seats', 'fuel_type', 'transmission', 'ac_status',
            'image_url', 'description', 'is_featured', 'is_active'
        ]
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Mahindra, Hyundai, Toyota, Tata', 'required': True}),
            'model': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Thar 4x4, Creta SX, Innova Crysta', 'required': True}),
            'vehicle_class': forms.Select(attrs={'class': 'form-select'}),
            'badge': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Popular Choice, 7-Seater, Luxury Executive, 4x4 Offroad'}),
            'price_per_day': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '3500', 'min': '1', 'required': True}),
            'security_deposit': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '3000', 'min': '0'}),
            'included_km': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '250', 'min': '0'}),
            'extra_km_rate': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '12', 'min': '0'}),
            'seats': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '5', 'min': '1', 'max': '20'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'transmission': forms.Select(attrs={'class': 'form-select'}),
            'ac_status': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Cold Climate Control A/C'}),
            'image_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://images.unsplash.com/... or vehicle photo link', 'id': 'carImageUrlInput'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Key features, trunk capacity, highway performance, cleanliness notes...'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-checkbox', 'id': 'isFeaturedCheckbox', 'style': 'width: 18px; height: 18px; cursor: pointer;'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox', 'id': 'isActiveCheckbox', 'style': 'width: 18px; height: 18px; cursor: pointer;'}),
        }


