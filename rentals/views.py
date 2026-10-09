from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date, datetime, timedelta
import urllib.parse

from .models import Location, Car, BookingRequest, Booking, CarReview
from .forms import BookingForm, BookingLookupForm, CarReviewForm, CarForm
from .services import NotificationService



def home_view(request):
    """Render public homepage with search widget, fleet showcase, and key benefits."""
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=2)).isoformat()
    
    featured_cars = Car.objects.filter(is_active=True, is_featured=True)[:4]
    if not featured_cars.exists():
        featured_cars = Car.objects.filter(is_active=True)[:4]
        
    locations = Location.objects.filter(is_active=True)

    return render(request, 'rentals/home.html', {
        'featured_cars': featured_cars,
        'locations': locations,
        'today': today,
        'tomorrow': tomorrow,
    })


def cars_list_view(request):
    """Render fleet catalog with live filtering and availability indicators."""
    cars_qs = Car.objects.filter(is_active=True)

    selected_class = request.GET.get('vehicle_class', '').strip()
    selected_trans = request.GET.get('transmission', '').strip()
    selected_fuel = request.GET.get('fuel_type', '').strip()
    search_query = request.GET.get('q', '').strip()
    pickup_date_str = request.GET.get('pickup_date', '').strip()
    return_date_str = request.GET.get('return_date', '').strip()

    if selected_class:
        cars_qs = cars_qs.filter(vehicle_class__iexact=selected_class)
    if selected_trans:
        cars_qs = cars_qs.filter(transmission__icontains=selected_trans)
    if selected_fuel:
        cars_qs = cars_qs.filter(fuel_type__iexact=selected_fuel)
    if search_query:
        cars_qs = cars_qs.filter(
            Q(brand__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(badge__icontains=search_query)
        )

    # Date availability filtering
    p_date = None
    r_date = None
    if pickup_date_str and return_date_str:
        try:
            p_date = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
            r_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    cars_list = []
    for car in cars_qs:
        car.is_available_selected = True
        if p_date and r_date:
            car.is_available_selected = car.is_available_for_dates(p_date, r_date)
        cars_list.append(car)

    locations = Location.objects.filter(is_active=True)

    return render(request, 'rentals/cars.html', {
        'cars': cars_list,
        'locations': locations,
        'selected_class': selected_class,
        'selected_trans': selected_trans,
        'selected_fuel': selected_fuel,
        'search_query': search_query,
        'pickup_date': pickup_date_str,
        'return_date': return_date_str,
    })


def car_detail_view(request, car_id):
    """Render car specification, rental terms, customer reviews/ratings, and direct booking trigger."""
    car = get_object_or_404(Car, id=car_id, is_active=True)
    locations = Location.objects.filter(is_active=True)
    similar_cars = Car.objects.filter(is_active=True, vehicle_class=car.vehicle_class).exclude(id=car.id)[:3]
    if not similar_cars.exists():
        similar_cars = Car.objects.filter(is_active=True).exclude(id=car.id)[:3]

    today = date.today().isoformat()
    default_return = (date.today() + timedelta(days=2)).isoformat()

    # Customer Reviews & Rating Analytics
    reviews = car.reviews.filter(is_approved=True).order_by('-created_at')
    total_reviews = reviews.count()
    
    # Rating breakdown
    breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        if r.rating in breakdown:
            breakdown[r.rating] += 1
            
    breakdown_pct = {}
    for star in [5, 4, 3, 2, 1]:
        count = breakdown[star]
        pct = int((count / total_reviews * 100)) if total_reviews > 0 else 0
        breakdown_pct[star] = {'count': count, 'pct': pct}

    # Pre-fill review form if coming from voucher/lookup
    ref_param = request.GET.get('review_ref', '').strip().upper()
    name_param = request.GET.get('name', '').strip()
    auto_open_review = bool(ref_param or request.GET.get('write_review'))
    initial_review_data = {
        'rating': 5,
        'booking_reference': ref_param,
        'customer_name': name_param,
    }
    review_form = CarReviewForm(initial=initial_review_data)

    return render(request, 'rentals/car_detail.html', {
        'car': car,
        'locations': locations,
        'similar_cars': similar_cars,
        'today': today,
        'default_return': default_return,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'breakdown_pct': breakdown_pct,
        'review_form': review_form,
        'auto_open_review': auto_open_review,
    })


def submit_car_review_view(request, car_id):
    """Handle review and star rating submission with name and booking reference verification."""
    car = get_object_or_404(Car, id=car_id, is_active=True)

    if request.method == 'POST':
        form = CarReviewForm(request.POST)
        if form.is_valid():
            customer_name = form.cleaned_data['customer_name'].strip()
            booking_ref = form.cleaned_data.get('booking_reference', '').strip().upper()
            rating = form.cleaned_data['rating']
            title = form.cleaned_data.get('title', '').strip()
            comment = form.cleaned_data['comment'].strip()
            trip_type = form.cleaned_data.get('trip_type', 'Vacation')

            # Verification logic using Booking Reference ID
            matching_booking = None
            is_verified = False
            customer_phone = ""
            if booking_ref:
                matching_booking = BookingRequest.objects.filter(booking_ref__iexact=booking_ref, car=car).first()
                if matching_booking:
                    is_verified = True
                    customer_phone = matching_booking.customer_phone or matching_booking.customer_mobile

            # Check if this booking was already reviewed
            if matching_booking and CarReview.objects.filter(booking=matching_booking).exists():
                existing_review = CarReview.objects.filter(booking=matching_booking).first()
                existing_review.rating = rating
                existing_review.title = title
                existing_review.comment = comment
                existing_review.trip_type = trip_type
                existing_review.customer_name = customer_name
                existing_review.save()
                messages.success(request, f"Thank you, {customer_name}! Your review for {car.brand} {car.model} has been updated.")
            else:
                CarReview.objects.create(
                    car=car,
                    booking=matching_booking,
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    rating=rating,
                    title=title,
                    comment=comment,
                    trip_type=trip_type,
                    is_verified_renter=is_verified,
                    is_approved=True
                )
                if is_verified:
                    messages.success(request, f"🌟 Thank you {customer_name}! Your Verified Renter review ({rating}★) for {car.brand} {car.model} is now live.")
                else:
                    messages.success(request, f"🌟 Thank you {customer_name}! Your review ({rating}★) for {car.brand} {car.model} has been published successfully.")

            from django.urls import reverse
            return redirect(f"{reverse('car_detail', args=[car.id])}#reviews")
        else:
            messages.error(request, "Please check your review submission fields and try again.")
            from django.urls import reverse
            return redirect(f"{reverse('car_detail', args=[car.id])}?write_review=1#write-review")

    return redirect('car_detail', car_id=car.id)


def booking_form_view(request, car_id):
    """Render guest checkout booking form with real-time pricing calculator and offline payment breakdown."""
    car = get_object_or_404(Car, id=car_id, is_active=True)
    locations = Location.objects.filter(is_active=True)
    
    pickup_date_param = request.GET.get('pickup_date', '')
    return_date_param = request.GET.get('return_date', '')

    today = date.today().isoformat()
    default_return = (date.today() + timedelta(days=2)).isoformat()

    return render(request, 'rentals/booking_form.html', {
        'car': car,
        'locations': locations,
        'today': today,
        'default_return': default_return,
        'pickup_date_param': pickup_date_param or today,
        'return_date_param': return_date_param or default_return,
    })


def booking_submit_view(request):
    """
    Handle 100% Guest Booking Submission:
    1. Direct guest details collection (name, phone, email, driving license).
    2. Overlap Availability Check (Prevent double booking).
    3. Automatic generation of Reference Code (KTF-YYYY-XXXX).
    4. Offline payment terms calculation & notification dispatch.
    """
    if request.method == 'POST':
        car_id = request.POST.get('car_id')
        car = get_object_or_404(Car, id=car_id)

        customer_name = request.POST.get('customer_name', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip() or request.POST.get('customer_mobile', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        driving_license_number = request.POST.get('driving_license_number', '').strip()

        pickup_loc_id = request.POST.get('pickup_location')
        pickup_location = None
        if pickup_loc_id:
            pickup_location = Location.objects.filter(id=pickup_loc_id).first()

        pickup_date_str = request.POST.get('pickup_date')
        pickup_time = request.POST.get('pickup_time', '10:00')
        return_date_str = request.POST.get('return_date')
        return_time = request.POST.get('return_time', '10:00')

        try:
            pickup_date_val = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pickup_date_val = date.today()

        try:
            return_date_val = datetime.strptime(return_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return_date_val = pickup_date_val + timedelta(days=2)

        # Ensure return date is not before pickup date
        if return_date_val < pickup_date_val:
            return_date_val = pickup_date_val

        # Fleet Availability Check
        if not car.is_available_for_dates(pickup_date_val, return_date_val):
            messages.error(
                request,
                f"Selected vehicle {car.brand} {car.model} is already booked from {pickup_date_val} to {return_date_val}. Please select alternative dates or choose another car from our fleet."
            )
            from django.urls import reverse
            return redirect(f"{reverse('booking_form', args=[car.id])}?pickup_date={pickup_date_val}&return_date={return_date_val}")

        policy_accepted = request.POST.get('policy_accepted') in ['on', 'true', '1', True]

        # Save directly to BookingRequest without requiring customer auth
        booking = BookingRequest.objects.create(
            user=None,
            car=car,
            customer_name=customer_name or "Guest Customer",
            customer_phone=customer_phone,
            customer_mobile=customer_phone,
            customer_whatsapp=customer_phone,
            customer_email=customer_email,
            driving_license_number=driving_license_number,
            pickup_location=pickup_location,
            pickup_date=pickup_date_val,
            pickup_time=pickup_time,
            return_date=return_date_val,
            return_time=return_time,
            policy_accepted=policy_accepted,
            status='PENDING',
            whatsapp_status='NOT_SENT'
        )

        # Dispatch automated confirmation notifications
        notif_result = NotificationService.send_automated_notifications(booking, 'REQUEST_SUBMITTED', request)

        return render(request, 'rentals/booking_submitted.html', {
            'car': car,
            'booking': booking,
            'booking_ref': booking.booking_ref,
            'customer_name': booking.customer_name,
            'customer_phone': booking.customer_phone,
            'customer_email': booking.customer_email,
            'pickup_location': booking.pickup_location.name if booking.pickup_location else "Main Hub",
            'pickup_date': booking.pickup_date.isoformat(),
            'pickup_time': booking.pickup_time,
            'return_date': booking.return_date.isoformat(),
            'return_time': booking.return_time,
            'total_days': booking.total_days,
            'net_rental_amount': booking.net_rental_amount,
            'security_deposit': booking.security_deposit,
            'payable_at_pickup': booking.payable_at_pickup,
            'whatsapp_direct_link': notif_result.get('whatsapp_link'),
        })

    return redirect('cars_list')


def booking_voucher_view(request, booking_ref):
    """Digital & printable rental voucher with complete offline payment breakdown and pickup details."""
    booking = get_object_or_404(BookingRequest.objects.select_related('car', 'pickup_location'), booking_ref=booking_ref)
    wa_direct = NotificationService.get_whatsapp_deep_link(booking, 'CONFIRMED' if booking.status == 'CONFIRMED' else 'REQUEST_SUBMITTED')

    return render(request, 'rentals/voucher.html', {
        'booking': booking,
        'car': booking.car,
        'wa_direct': wa_direct,
    })


def booking_lookup_view(request):
    """
    Guest booking tracking view.
    Allows guests to retrieve their booking, view status, and download their voucher
    using booking_reference (or booking_ref) and customer_phone (or mobile).
    """
    booking = None
    searched = False

    if request.method == 'POST':
        ref = (request.POST.get('booking_reference') or request.POST.get('booking_ref', '')).strip().upper()
        phone_input = (request.POST.get('customer_phone') or request.POST.get('mobile', '')).strip()
        searched = True

        if ref and phone_input:
            clean_digits = ''.join(filter(str.isdigit, phone_input))
            # Match by reference code
            candidates = BookingRequest.objects.filter(booking_ref__iexact=ref).select_related('car', 'pickup_location')
            for b in candidates:
                b_phone = ''.join(filter(str.isdigit, b.customer_phone or b.customer_mobile or b.customer_whatsapp))
                if clean_digits in b_phone or b_phone in clean_digits or b.customer_phone == phone_input:
                    booking = b
                    break

            if not booking:
                messages.error(request, "No booking found matching this Reference ID and Phone Number combination.")
        else:
            messages.error(request, "Please provide both your Booking Reference ID and registered Phone Number.")

        form = BookingLookupForm(initial={'booking_reference': ref, 'customer_phone': phone_input})
    else:
        # Pre-fill if passed via GET query params
        ref_param = request.GET.get('ref', '').strip().upper()
        phone_param = request.GET.get('phone', '').strip()
        form = BookingLookupForm(initial={'booking_reference': ref_param, 'customer_phone': phone_param})
        if ref_param and phone_param:
            clean_digits = ''.join(filter(str.isdigit, phone_param))
            candidates = BookingRequest.objects.filter(booking_ref__iexact=ref_param).select_related('car', 'pickup_location')
            for b in candidates:
                b_phone = ''.join(filter(str.isdigit, b.customer_phone or b.customer_mobile or b.customer_whatsapp))
                if clean_digits in b_phone or b_phone in clean_digits:
                    booking = b
                    searched = True
                    break

    return render(request, 'rentals/booking_lookup.html', {
        'form': form,
        'booking': booking,
        'searched': searched,
    })


def cancel_booking_view(request, booking_ref):
    """Allows guests to cancel their reservation with offline verification."""
    booking = get_object_or_404(BookingRequest, booking_ref=booking_ref)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Cancelled by customer via portal')
        booking.status = 'CANCELLED'
        booking.cancellation_reason = reason
        booking.save()

        # Trigger notification
        NotificationService.send_automated_notifications(booking, 'CANCELLED', request)

        messages.success(request, f"Booking {booking.booking_ref} has been cancelled successfully. No charges apply.")
        return redirect('booking_voucher', booking_ref=booking.booking_ref)

    return redirect('booking_voucher', booking_ref=booking.booking_ref)


# -------------------------------------------------------------------
# Static Legal & Informational Pages
# -------------------------------------------------------------------

def contact_view(request):
    """Render contact and pickup location information."""
    locations = Location.objects.filter(is_active=True)
    return render(request, 'rentals/contact.html', {
        'locations': locations,
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


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# Owner Authentication & Dashboard Views (Staff / Superusers)
# -------------------------------------------------------------------

def owner_login_view(request):
    """Owner & Fleet Manager authentication portal."""
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_shell_preview')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}! You are now logged into the Owner Operations Dashboard.")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('admin_shell_preview')
        else:
            messages.error(request, "Invalid owner username or password. Please try again.")

    return render(request, 'rentals/login.html', {
        'next': request.GET.get('next', ''),
    })


def owner_logout_view(request):
    """Log out of owner dashboard."""
    logout(request)
    messages.info(request, "You have been logged out of the Owner Dashboard.")
    return redirect('home')


@login_required(login_url='owner_login')
def admin_shell_preview_view(request):
    """Owner Operations Control Dashboard with live actions and automated notifications."""
    if request.method == 'POST':
        action = request.POST.get('action')
        booking_id = request.POST.get('booking_id')
        if booking_id:
            booking = get_object_or_404(BookingRequest, id=booking_id)
            if action == 'confirm':
                booking.status = 'CONFIRMED'
                booking.save()
                NotificationService.send_automated_notifications(booking, 'CONFIRMED', request)
                messages.success(request, f"Booking {booking.booking_ref} marked as CONFIRMED. Customer notified.")
            elif action == 'reject':
                booking.status = 'REJECTED'
                booking.save()
                NotificationService.send_automated_notifications(booking, 'REJECTED', request)
                messages.warning(request, f"Booking {booking.booking_ref} marked as REJECTED. Customer notified.")
            elif action == 'mark_whatsapp_sent':
                booking.whatsapp_status = 'SENT'
                booking.save()
                messages.success(request, f"WhatsApp confirmation marked as SENT for {booking.booking_ref}.")
        return redirect('admin_shell_preview')

    status_filter = request.GET.get('status', '').strip()
    bookings_qs = BookingRequest.objects.select_related('car', 'pickup_location').all()

    if status_filter:
        bookings_qs = bookings_qs.filter(status=status_filter)

    pending_count = BookingRequest.objects.filter(status='PENDING').count()
    confirmed_count = BookingRequest.objects.filter(status='CONFIRMED').count()
    total_cars_count = Car.objects.filter(is_active=True).count()
    pending_wa_count = BookingRequest.objects.filter(status='CONFIRMED', whatsapp_status='NOT_SENT').count()

    # Pre-generate rich WhatsApp helper links
    bookings_list = []
    for b in bookings_qs[:25]:
        event_type = 'CONFIRMED' if b.status == 'CONFIRMED' else ('REJECTED' if b.status == 'REJECTED' else 'REQUEST_SUBMITTED')
        b.wa_link = NotificationService.get_whatsapp_deep_link(b, event_type)
        bookings_list.append(b)

    return render(request, 'rentals/admin_shell.html', {
        'bookings': bookings_list,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'total_cars_count': total_cars_count,
        'pending_wa_count': pending_wa_count,
        'status_filter': status_filter,
    })


@login_required(login_url='owner_login')
def admin_manage_cars_view(request):
    """Dedicated Owner/Staff Fleet Management view with status toggles and Django admin links."""
    if request.method == 'POST':
        action = request.POST.get('action')
        car_id = request.POST.get('car_id')
        if car_id:
            car = get_object_or_404(Car, id=car_id)
            if action == 'toggle_active':
                car.is_active = not car.is_active
                car.save()
                status_str = "Active (Visible to Renters)" if car.is_active else "Inactive (Hidden from Renters)"
                messages.success(request, f"{car.brand} {car.model} is now {status_str}.")
            elif action == 'toggle_featured':
                car.is_featured = not car.is_featured
                car.save()
                feat_str = "Featured on Homepage" if car.is_featured else "Standard Fleet"
                messages.success(request, f"{car.brand} {car.model} is now {feat_str}.")
        return redirect('admin_manage_cars')

    cars = Car.objects.all().order_by('-is_active', 'brand', 'model')
    total_cars = cars.count()
    active_cars = cars.filter(is_active=True).count()
    inactive_cars = cars.filter(is_active=False).count()
    featured_cars = cars.filter(is_featured=True).count()

    return render(request, 'rentals/admin_cars.html', {
        'cars': cars,
        'total_cars': total_cars,
        'active_cars': active_cars,
        'inactive_cars': inactive_cars,
        'featured_cars': featured_cars,
    })


@login_required(login_url='owner_login')
def admin_car_create_view(request):
    """Allow owner to add a new vehicle directly into the fleet from the custom portal."""
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save()
            status_visibility = "and is immediately live on the customer portal" if car.is_active else "(set as inactive/hidden)"
            messages.success(
                request,
                f"🎉 {car.brand} {car.model} successfully added to the fleet {status_visibility}!"
            )
            return redirect('admin_manage_cars')
        else:
            messages.error(request, "Please correct the errors in the form before saving.")
    else:
        # Default placeholder sample image if empty
        form = CarForm(initial={
            'price_per_day': 3000,
            'security_deposit': 3000,
            'included_km': 250,
            'extra_km_rate': 12,
            'seats': 5,
            'is_active': True,
            'is_featured': False,
            'image_url': 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=800&auto=format&fit=crop&q=80',
        })

    return render(request, 'rentals/admin_car_form.html', {
        'form': form,
        'is_edit': False,
        'car': None,
    })


@login_required(login_url='owner_login')
def admin_car_edit_view(request, car_id):
    """Allow owner to edit vehicle specs, pricing, photos, and visibility directly from the portal."""
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            car = form.save()
            messages.success(
                request,
                f"✅ {car.brand} {car.model} updated successfully! Changes are instantly reflected on customer search and booking pages."
            )
            return redirect('admin_manage_cars')
        else:
            messages.error(request, "Please fix the validation errors below.")
    else:
        form = CarForm(instance=car)

    return render(request, 'rentals/admin_car_form.html', {
        'form': form,
        'is_edit': True,
        'car': car,
    })


@login_required(login_url='owner_login')
def admin_car_delete_view(request, car_id):
    """Allow owner to delete or decommission a car from fleet."""
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        car_name = f"{car.brand} {car.model}"
        # If there are active/confirmed bookings, warn and allow safe deactivation or deletion
        active_bookings_count = car.bookings.filter(status__in=['PENDING', 'CONFIRMED']).count()
        if active_bookings_count > 0:
            # Safe action: deactivate instead of hard delete to preserve booking references
            car.is_active = False
            car.save()
            messages.warning(
                request,
                f"⚠️ {car_name} has {active_bookings_count} active/pending booking(s). It has been deactivated and hidden from customers instead of permanently deleted to preserve rental vouchers."
            )
        else:
            car.delete()
            messages.success(request, f"🗑️ {car_name} was removed from the fleet.")
    return redirect('admin_manage_cars')


