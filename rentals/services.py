import logging
import urllib.parse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Automated notification engine for Keys to your freedom car rentals.
    Handles multi-channel notifications (Email & WhatsApp) with clear offline payment notices.
    """

    @staticmethod
    def get_business_contact():
        return {
            'name': 'Keys to your freedom',
            'phone': '+91 98765 43210',
            'whatsapp': '+919876543210',
            'email': 'rentals@keystoyourfreedom.com',
            'payment_instructions': 'Payment is due offline upon physical vehicle inspection (Cash or UPI). No online advance payment required.'
        }

    @classmethod
    def generate_whatsapp_text(cls, booking, event_type='REQUEST_SUBMITTED'):
        """
        Generate rich WhatsApp formatted text for instant customer notifications and owner follow-up.
        """
        biz = cls.get_business_contact()
        
        if event_type == 'CONFIRMED':
            text = (
                f"🎉 *BOOKING CONFIRMED — {biz['name']}*\n\n"
                f"Dear {booking.customer_name},\n"
                f"Your vehicle booking is *CONFIRMED*!\n\n"
                f"📋 *Booking Ref:* `{booking.booking_ref}`\n"
                f"🚗 *Vehicle:* {booking.car.brand} {booking.car.model} ({booking.car.vehicle_class})\n"
                f"📅 *Pickup:* {booking.pickup_date} at {booking.pickup_time}\n"
                f"📍 *Pickup Point:* {booking.pickup_location.name if booking.pickup_location else 'Main Terminal'}\n"
                f"📅 *Return:* {booking.return_date} at {booking.return_time}\n"
                f"🛣️ *Included KM:* {booking.total_free_km} KM\n\n"
                f"💰 *Offline Payment Summary:*\n"
                f"• Rental Fee ({booking.total_days} days): ₹{booking.net_rental_amount:,}\n"
                f"• Refundable Security Deposit: ₹{booking.security_deposit:,}\n"
                f"• *Total Due at Pickup:* ₹{booking.payable_at_pickup:,}\n\n"
                f"ℹ️ *Payment Method:* Pay upon pickup via *UPI or Cash* after verifying the car.\n"
                f"📄 Please carry your original Driving License and Aadhaar/Govt ID.\n\n"
                f"📞 Helpdesk: {biz['phone']}\n"
                f"Enjoy your drive with {biz['name']}!"
            )
        elif event_type == 'REJECTED':
            text = (
                f"⚠️ *BOOKING UPDATE — {biz['name']}*\n\n"
                f"Dear {booking.customer_name},\n"
                f"We regret to inform you that vehicle *{booking.car.brand} {booking.car.model}* is currently unavailable for your selected dates ({booking.pickup_date} to {booking.return_date}).\n\n"
                f"Ref: `{booking.booking_ref}`\n"
                f"Please reply or contact us at {biz['phone']} to view alternative available vehicles."
            )
        elif event_type == 'CANCELLED':
            text = (
                f"ℹ️ *BOOKING CANCELLED — {biz['name']}*\n\n"
                f"Dear {booking.customer_name},\n"
                f"Your booking reference `{booking.booking_ref}` has been successfully cancelled.\n"
                f"No cancellation fees apply for offline reservations. We hope to serve you again soon!"
            )
        else: # REQUEST_SUBMITTED (default)
            text = (
                f"🚗 *BOOKING REQUEST RECEIVED — {biz['name']}*\n\n"
                f"Dear {booking.customer_name},\n"
                f"Thank you for requesting a self-drive rental with *{biz['name']}*!\n\n"
                f"📋 *Ref ID:* `{booking.booking_ref}`\n"
                f"🚘 *Car:* {booking.car.brand} {booking.car.model}\n"
                f"📅 *Dates:* {booking.pickup_date} ({booking.pickup_time}) to {booking.return_date} ({booking.return_time})\n"
                f"📍 *Pickup Location:* {booking.pickup_location.name if booking.pickup_location else 'Main Terminal'}\n"
                f"💵 *Payable on Pickup (UPI/Cash):* ₹{booking.payable_at_pickup:,}\n\n"
                f"⏳ *Status:* Pending confirmation. Our fleet manager will verify and confirm within 15 minutes."
            )
        return text

    @classmethod
    def get_whatsapp_deep_link(cls, booking, event_type='REQUEST_SUBMITTED'):
        """Create clickable wa.me direct link with pre-encoded message text."""
        raw_phone = str(booking.customer_whatsapp or booking.customer_mobile)
        phone = ''.join(filter(str.isdigit, raw_phone))
        message = cls.generate_whatsapp_text(booking, event_type)
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{phone}?text={encoded_message}"

    @classmethod
    def send_automated_notifications(cls, booking, event_type='REQUEST_SUBMITTED', request=None):
        """
        Trigger both email dispatch and WhatsApp automation recording.
        """
        results = {'email_sent': False, 'whatsapp_link': cls.get_whatsapp_deep_link(booking, event_type)}

        # 1. Email Notification Dispatch
        if booking.customer_email:
            try:
                subject_map = {
                    'REQUEST_SUBMITTED': f"Booking Request Received — {booking.booking_ref} | Keys to your freedom",
                    'CONFIRMED': f"🎉 Booking Confirmed! Ref: {booking.booking_ref} | Keys to your freedom",
                    'REJECTED': f"Booking Update: {booking.booking_ref} | Keys to your freedom",
                    'CANCELLED': f"Booking Cancelled: {booking.booking_ref} | Keys to your freedom",
                }
                subject = subject_map.get(event_type, f"Booking Update — {booking.booking_ref}")
                
                plain_body = cls.generate_whatsapp_text(booking, event_type)
                
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'rentals@keystoyourfreedom.com')
                send_mail(
                    subject=subject,
                    message=plain_body,
                    from_email=from_email,
                    recipient_list=[booking.customer_email],
                    fail_silently=True
                )
                booking.email_status = 'SENT'
                booking.save(update_fields=['email_status'])
                results['email_sent'] = True
            except Exception as e:
                logger.error(f"Failed to send email to {booking.customer_email}: {e}")
                booking.email_status = 'FAILED'
                booking.save(update_fields=['email_status'])

        return results
