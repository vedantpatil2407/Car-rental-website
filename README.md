# Keys to your freedom 🚗

A production-ready, owner-controlled car rental website built for a small local rental business.

The website is designed as a **lead-generation + booking-request system**, not an instant-booking marketplace.

---

## 🚗 Project Overview

**Keys to your freedom** allows customers to:

* Browse available rental cars
* View car details, pricing and images
* Select pickup and return dates/times
* Select a pickup location/hub
* Submit a rental booking request
* Accept the rental responsibility policy
* Receive a booking reference
* Contact the owner through WhatsApp or phone

The owner/admin controls:

* Cars
* Pricing
* Availability
* Booking requests
* Confirmations/rejections
* Offline payments
* Deposits/security records
* Maintenance/unavailability blocks
* Pickup locations
* Rental policy
* Booking summaries and PDFs

> **Important:** V1 does NOT provide instant booking or online payment.

A booking request is **not a confirmed booking** until the owner manually confirms it.

---

# 🎯 V1 Goals

The first version should be:

* Production-ready
* Mobile-first
* Fast and simple
* Easy for the owner to operate
* Low-cost to host
* Secure
* Easy to maintain
* Suitable for a small owner-operated rental business

The system should avoid unnecessary complexity.

---

# 🧑‍💻 Technology Stack

## Backend

* Python
* Django
* Django Templates
* Django Admin

## Frontend

* HTML
* CSS
* Vanilla JavaScript

No unnecessary frontend framework for V1.

## Database

Development:

* SQLite

Production:

* Neon PostgreSQL

## Car Images

* Cloudinary

Car images must not depend on temporary Render local storage.

## Hosting

* Render

## Domain / DNS

* Cloudflare
* Custom domain

## Version Control

* Git
* GitHub

---

# 🎨 UI / Design Direction

The website should have a:

**Dark premium automotive mobile-first design.**

### Main visual direction

* Dark navy / near-black background
* Cyan primary actions
* Orange/yellow highlights
* Green WhatsApp/success actions
* Red danger/error actions
* Premium automotive feel
* Clean typography
* Strong car photography
* Rounded modern cards
* Clear pricing
* Pill-style status indicators

The design should be inspired by the provided reference and implemented consistently throughout the website.

### Mobile

The website must be fully responsive.

On mobile:

* Easy thumb-friendly controls
* Large CTA buttons
* Clean booking form
* Easy WhatsApp/Call access
* Mobile navigation where appropriate
* No horizontal scrolling

---

# 👤 Customer Website

## Home Page

Should include:

* Brand/logo
* Hero section
* Main CTA
* Featured cars
* Why choose us
* Rental process
* Pickup information
* Contact section
* WhatsApp CTA
* Call CTA

---

# 🚘 Cars

Customers can browse rental cars.

Each car should support:

* Name
* Brand
* Model
* Year
* Registration/display identifier where appropriate
* Image(s)
* Description
* Seating capacity
* Fuel type
* Transmission
* Rental price
* Status
* Features

### Car Status

Supported statuses:

```text
ACTIVE
INACTIVE
MAINTENANCE
```

Only `ACTIVE` cars should be available for customer booking requests.

---

# 📅 Availability

Availability must be handled centrally.

Use one reusable function:

```python
is_car_available(car, pickup_datetime, return_datetime)
```

The system must prevent overlapping confirmed bookings and unavailable blocks.

### Overlap rule

Two time periods overlap when:

```text
existing_start < requested_end
AND
existing_end > requested_start
```

### Important rules

* `PENDING` booking does NOT block availability.
* `REJECTED` booking does NOT block availability.
* `CANCELLED` booking does NOT block availability.
* Only `CONFIRMED` bookings block the car.
* Maintenance/unavailable blocks also block the car.
* Inactive cars cannot be booked.
* Owner must re-check availability before confirming.

---

# 📝 Booking Request Flow

Customer selects:

* Car
* Pickup date
* Pickup time
* Return date
* Return time
* Pickup location

Then enters:

* Full name
* Mobile number
* WhatsApp number
* Email (optional)
* Preferred contact method
* Message/notes

The customer must accept the final rental responsibility policy before submitting.

---

# ⚠️ Booking Is NOT Instant

After submission:

```text
Customer
   ↓
Booking Request
   ↓
PENDING
   ↓
Owner reviews
   ↓
Availability rechecked
   ↓
CONFIRMED / REJECTED
```

The customer must clearly see that:

> **Submitting a request does not confirm the rental.**

The submitted page should provide:

* Booking reference
* WhatsApp Owner button
* Call Owner button
* Clear pending/not-confirmed message

---

# 🔖 Booking Reference

Use a readable booking reference such as:

```text
KTF-2026-0001
```

The format should be unique and easy to communicate.

---

# 📊 Booking Statuses

Supported booking statuses:

```text
PENDING
CONFIRMED
REJECTED
CANCELLED
COMPLETED
```

### PENDING

Customer submitted a request.

Does not block availability.

### CONFIRMED

Owner manually confirmed the booking.

Blocks availability.

### REJECTED

Owner rejected the request.

Does not block availability.

### CANCELLED

Booking was cancelled.

Does not block availability.

### COMPLETED

Rental has been completed.

---

# 🛠️ Admin Dashboard

The owner should have a clean admin dashboard.

Dashboard should provide:

* Booking statistics
* Pending requests
* Confirmed bookings
* Upcoming pickups
* Upcoming returns
* Cars
* Availability
* Manual blocks
* Payments
* Deposits
* Rental policy
* Pickup locations

---

# 📆 Availability Blocks

Owner can manually block a car.

Block reasons:

```text
OFFLINE_BOOKING
RESERVED
MAINTENANCE
PERSONAL_USE
UNAVAILABLE
CLEANING
OTHER
```

A manual availability block should contain:

* Car
* Start datetime
* End datetime
* Reason
* Notes

---

# 🚗 Pickup Location

V1 supports pickup hubs/locations.

No vehicle delivery system is required for V1.

Pickup location should be configurable by the owner.

Configuration may include:

* Name
* Address
* Maps link/embed
* Phone
* WhatsApp
* Pickup instructions

---

# 💰 Payments

There is **NO online payment gateway in V1**.

Do not add:

* Razorpay
* Stripe
* Automatic online payments

Payment happens offline after confirmation/pickup according to the owner's process.

Admin should be able to maintain:

* Rental total
* Amount paid
* Balance
* Payment status
* Payment notes

---

# 🔐 Deposit / Security

Security deposit information is maintained manually by the owner.

The deposit should be an admin-controlled record.

Customers should not upload documents publicly for the deposit workflow in V1.

---

# 📜 Responsibility Policy

Before submitting a booking request, the customer must accept the rental responsibility policy.

The policy is:

* Compact
* Clearly visible
* Unchecked by default
* Required for submission

The system must store:

* Policy version
* Policy title
* Exact policy text snapshot
* Acceptance timestamp
* Optional IP address
* Optional user-agent

The policy may include renter responsibility for attributable damage and accident-related charges, subject to the agreed rental terms and applicable law.

Accepting the policy:

> Does NOT mean the booking is confirmed.

It only records that the customer accepted the displayed policy while submitting the request.

The owner should be able to edit the policy from settings when practical.

---

# 📄 Confirmed Booking PDF

After a booking is confirmed, the system should generate a branded booking summary/PDF.

The PDF should contain relevant booking information such as:

* Business name
* Booking reference
* Customer details
* Car
* Pickup information
* Return information
* Rental amount
* Payment information
* Deposit information where applicable
* Accepted responsibility policy snapshot
* Confirmation details

The PDF should be available for download/share.

---

# 💬 WhatsApp Workflow

WhatsApp should be handled through user-initiated `wa.me` links.

The system must NOT claim that it automatically sends WhatsApp messages or attachments.

After confirmation, the admin may use:

**Confirm Booking & Send WhatsApp**

This opens WhatsApp with a prefilled confirmation message.

The owner must manually press Send.

Possible workflow:

```text
Owner confirms booking
        ↓
Booking summary generated
        ↓
WhatsApp opens
        ↓
Prefilled confirmation message
        ↓
Owner presses Send
```

The same principle applies to sharing the booking PDF.

---

# ☎️ Contact

The website should provide clear:

* Call Owner
* WhatsApp Owner

actions.

Phone number and WhatsApp number should be configurable rather than hard-coded throughout the application.

---

# ⚙️ Business Settings

Important business information should be configurable.

Examples:

* Business name
* Phone
* WhatsApp
* Email
* Address
* Maps link
* Pickup instructions
* Rental policy
* Social links
* Currency
* Default settings

Official business name:

```text
Keys to your freedom
```

---

# 🗄️ Database

Production database:

**Neon PostgreSQL**

Important entities should include concepts for:

* Cars
* Car images
* Bookings
* Availability blocks
* Pickup locations
* Business settings
* Rental responsibility policy
* Policy acceptance
* Payments
* Deposits

The exact Django model implementation can be refined during development without changing the required business logic.

---

# 🔒 Security

The production application must include:

* Django authentication
* Admin access protection
* CSRF protection
* Server-side validation
* Proper form validation
* Secure environment variables
* No secrets committed to GitHub
* Production `DEBUG=False`
* Secure production configuration
* Database credentials stored in environment variables
* Proper permission checks
* Customer data protection

Never expose sensitive admin information publicly.

---

# 🖼️ Image Storage

Car images should use Cloudinary in production.

Reason:

Render's local filesystem should not be treated as permanent storage for uploaded car images.

The application should allow the owner to manage car images without needing to modify source code.

---

# 🚀 Deployment Architecture

```text
Customer
   ↓
Custom Domain
   ↓
Cloudflare
   ↓
Render
   ↓
Django Application
   ↓
Neon PostgreSQL
   +
Cloudinary
```

---

# 🌐 Production Deployment

Production deployment should include:

* Render web service
* Neon PostgreSQL database
* Cloudinary media storage
* Cloudflare DNS
* Custom domain
* HTTPS
* Environment variables
* Production Django settings

---

# 🧪 Testing / QA

Before considering V1 complete, test:

### Customer

* Home page
* Car browsing
* Car details
* Booking form
* Required fields
* Policy checkbox
* Booking submission
* Booking reference
* WhatsApp link
* Call link
* Mobile responsiveness

### Availability

* Same-time overlap
* Partial overlap
* Existing booking around requested time
* Adjacent bookings
* Maintenance blocks
* Manual unavailable blocks
* Pending booking behavior
* Cancelled booking behavior
* Confirmed booking behavior

### Admin

* Login
* Car CRUD
* Booking management
* Availability blocks
* Confirmation
* Rejection
* Cancellation
* Completion
* Payment records
* Deposit records
* Policy management

### PDF

* Correct booking information
* Correct customer information
* Correct policy snapshot
* Correct totals
* Professional formatting

### Mobile

Test on real mobile devices and different screen sizes.

---

# 🔍 SEO / Production Quality

Include basic production SEO:

* Proper page titles
* Meta descriptions
* Semantic HTML
* Open Graph metadata where appropriate
* Favicon
* Clean URLs
* Proper error pages

The website should feel like a real local business website, not a demo project.

---

# 🧠 Development Principles

1. Do not unnecessarily overwrite working code.
2. Do not simplify away production requirements.
3. Do not introduce unnecessary dependencies.
4. Keep the application maintainable.
5. Keep business logic centralized.
6. Validate important actions on the server.
7. Test every major feature before moving forward.
8. Keep Git commits organized.
9. Never commit secrets.
10. Preserve existing working features when adding new ones.

---

# 🛠️ Development Workflow

The project workflow is:

```text
Stitch
   ↓
Claude
   ↓
Antigravity
   ↓
GitHub
   ↓
Neon PostgreSQL
   ↓
Cloudinary
   ↓
Render
   ↓
Cloudflare / Custom Domain
```

---

# 🧩 Antigravity Development Phases

Development should happen in **5 controlled parts**.

## Part 1 — UI

Build/refine:

* Overall layout
* Dark premium automotive theme
* Home page
* Cars
* Car cards
* Booking UI
* Responsive/mobile design
* Navigation
* Buttons
* Forms
* Admin visual structure

After completing Part 1:

* Test the UI
* Fix obvious issues
* Commit changes
* STOP

Wait for permission before starting Part 2.

---

## Part 2 — Cars & Availability

Implement:

* Car models
* Car management
* Car images
* Car statuses
* Availability logic
* Confirmed booking blocking
* Availability blocks
* Maintenance handling
* Pickup locations

Test overlap logic carefully.

Commit changes.

STOP and wait for permission.

---

## Part 3 — Booking & Responsibility Policy

Implement:

* Customer booking form
* Validation
* Booking references
* PENDING workflow
* Responsibility policy
* Policy acceptance snapshot
* Customer confirmation/pending page
* WhatsApp/Call actions

Important:

Submitting a request must never automatically confirm the booking.

Commit changes.

STOP and wait for permission.

---

## Part 4 — Admin, Confirmation & PDF

Implement:

* Admin dashboard
* Booking management
* Confirm/reject/cancel/complete
* Availability recheck before confirmation
* Payment records
* Deposit records
* Booking summary
* PDF generation
* WhatsApp confirmation workflow

Test the complete booking lifecycle.

Commit changes.

STOP and wait for permission.

---

## Part 5 — Deployment & QA

Implement/configure:

* Production settings
* Neon PostgreSQL
* Cloudinary
* Render
* Cloudflare
* Custom domain
* HTTPS
* Environment variables
* Security
* SEO
* Error pages

Then perform complete QA.

Test:

```text
Customer → Request → Pending → Admin Review
→ Availability Check → Confirm
→ PDF → WhatsApp Workflow
```

Also test rejection, cancellation, maintenance and overlapping bookings.

---

# 📌 Important V1 Exclusions

The following are intentionally **NOT part of V1**:

* Instant booking
* Online payment gateway
* Razorpay
* Stripe
* Automatic WhatsApp API
* Server-side automatic WhatsApp sending
* Customer-direct booking confirmation
* Public document upload
* Vehicle delivery system
* Complex marketplace features

The goal is a reliable, simple, owner-controlled rental system.

---

# 🎯 Final V1 Definition

The finished application should allow:

```text
Customer
   ↓
Browse Cars
   ↓
Select Dates + Pickup
   ↓
Submit Request
   ↓
Accept Responsibility Policy
   ↓
PENDING
   ↓
Owner Reviews
   ↓
Availability Rechecked
   ↓
CONFIRMED / REJECTED
   ↓
If Confirmed:
Booking Summary + PDF
   ↓
Owner-Initiated WhatsApp Workflow
   ↓
Rental
   ↓
COMPLETED
```

The final product should be **production-ready, mobile-first, secure, maintainable and suitable for a real small local car-rental business.**

---

## 🚗 Keys to your freedom

**Real cars. Real bookings. Simple process.**
