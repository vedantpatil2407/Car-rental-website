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
