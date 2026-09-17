# MASTER PROMPT — “Keys to your freedom” Car Rental Website

## 0. ROLE

You are acting as the senior:

* Software Architect
* Product Manager
* UI/UX Engineer
* Django/Python Engineer
* Database Architect
* Security Engineer
* QA/Test Engineer
* DevOps/Deployment Engineer

You are responsible for building a real-world, production-ready car-rental website for a small local rental business.

The website must be practical, maintainable, secure, responsive, and easy for a non-technical business owner to operate.

Do not build an unnecessarily complicated system.

The system must prioritize:

1. Correct business logic
2. Real availability
3. Manual owner control
4. Simple customer booking
5. Clear communication
6. Security
7. Maintainability
8. Mobile responsiveness
9. Production deployment readiness

---

# 1. BUSINESS IDENTITY

## Confirmed Business Name

The official and confirmed business name for this project is:

**Keys to your freedom**

This is NOT a placeholder.

Do not ask the project owner to replace, confirm, or choose another business name.

Use the exact business name:

**Keys to your freedom**

consistently throughout the project.

This includes:

* Website navbar
* Logo/brand text
* Homepage
* Footer
* Page titles
* Booking pages
* Contact page
* About page
* Rental rules
* Admin dashboard branding
* Admin login
* Customer communication
* WhatsApp message templates
* Booking confirmation/rejection communication
* Browser/page metadata where appropriate
* Emails/messages if added later
* Any customer-facing text
* Any business-facing dashboard branding

Store the business name in:

`BusinessSettings.business_name`

The initial seeded/default value must be:

`Keys to your freedom`

The business name should remain editable from the admin settings in the future, but it must NOT be replaced automatically.

Do not hardcode the business name in dozens of templates.

Use the configured `BusinessSettings.business_name` wherever possible.

If the settings value is missing, use:

`Keys to your freedom`

as the safe default.

Do not introduce another fictional business name.

---

# 2. BUSINESS MODEL

This is a small local car-rental business.

The website is NOT an instant online car-booking/payment marketplace.

The core business model is:

Customer browses cars → selects dates → submits booking request → immediately contacts owner through WhatsApp/phone → owner manually verifies and confirms → customer pays offline → customer picks up vehicle → vehicle is returned → owner completes the booking.

The most important business rule is:

**Submitting a booking request does NOT mean the booking is confirmed.**

A customer must never be told that their booking is confirmed merely because they submitted a form.

---

# 3. NON-NEGOTIABLE BOOKING RULE

A customer booking request initially has:

`PENDING`

status.

The customer sees:

> Your booking request has been received. Your booking is NOT confirmed yet.

The customer must contact the owner using:

* WhatsApp
* Phone call

The website must NOT tell the customer:

* “The owner will call you”
* “Your booking is confirmed”
* “Your car is reserved”
* “Payment successful”
* “Booking successful”

unless the appropriate business action has actually occurred.

WhatsApp and phone are communication channels.

They are NOT automatic booking confirmation mechanisms.

Only an authenticated owner/admin can change:

`PENDING → CONFIRMED`

---

# 4. CUSTOMER BOOKING FLOW

The customer journey should be:

1. Open website
2. Browse available cars
3. Select rental dates
4. Select pickup location/hub
5. View cars available for that date range
6. Open car details
7. Click Book / Request Booking
8. Fill customer details
9. Submit booking request
10. Booking receives unique reference code
11. Booking is created as `PENDING`
12. Customer is shown booking-submitted page
13. Customer immediately gets:

* WhatsApp Owner button
* Call Owner button

14. Customer contacts owner
15. Owner verifies availability/details manually
16. Owner opens admin dashboard
17. Owner performs live availability check
18. Owner confirms or rejects booking
19. If confirmed, owner can use a WhatsApp deep link/message to notify customer
20. Payment happens offline
21. Security deposit is handled offline
22. Customer physically collects vehicle
23. Customer returns vehicle
24. Owner inspects vehicle
25. Owner settles security deposit
26. Owner marks booking `COMPLETED`

---

# 5. BOOKING STATUS SYSTEM

Use the following statuses:

* `PENDING`
* `CONFIRMED`
* `REJECTED`
* `CANCELLED`
* `COMPLETED`

## PENDING

Customer submitted a request.

It is not confirmed.

It must NOT block the car from being considered available.

Multiple pending requests may overlap.

The admin should be warned about overlapping pending requests.

## CONFIRMED

Owner/admin manually confirmed the booking.

A confirmed booking blocks that car for its rental period.

## REJECTED

Owner/admin rejected the request.

It does not block availability.

## CANCELLED

A previously confirmed booking was cancelled.

It no longer blocks availability according to the cancellation logic.

## COMPLETED

The rental has finished and the vehicle has been returned.

Historical booking data must remain preserved.

---

# 6. AVAILABILITY — CRITICAL BUSINESS LOGIC

Availability is one of the most important parts of this project.

A car is bookable only when:

1. The car's global status is `ACTIVE`
2. There is no manual availability block overlapping the requested period
3. There is no `CONFIRMED` booking overlapping the requested period

Pending bookings do NOT block availability.

---

# 7. TWO-LAYER AVAILABILITY SYSTEM

Availability must have two separate layers.

## Layer 1 — Global Car Status

Possible values:

* `ACTIVE`
* `INACTIVE`
* `MAINTENANCE`

An inactive/maintenance vehicle must not be publicly bookable.

## Layer 2 — Date-Specific Availability

Use:

`AvailabilityBlock`

This allows the owner to manually block a vehicle for a specific date/time range.

Reasons can include:

* Offline booking
* Reserved
* Maintenance
* Personal use
* Vehicle unavailable
* Cleaning/service
* Other

Example:

Owner wants to block a Swift from:

20 September → 25 September

without creating a customer booking.

The owner must be able to create a manual availability block.

During that period the Swift must disappear from available public search results.

Outside that period, it becomes available again.

This functionality is independent of bookings.

---

# 8. AVAILABILITY OVERLAP LOGIC

Implement reusable server-side availability logic.

Do not duplicate availability logic across views.

Create a central service/helper such as:

`is_car_available(car, pickup_datetime, return_datetime)`

or an equivalent clean service-layer implementation.

The logic must check:

* Global car status
* Manual availability blocks
* Confirmed bookings

Pending bookings must not block availability.

Use proper datetime overlap logic.

A typical overlap condition is:

`existing_start < requested_end AND existing_end > requested_start`

Handle date/time boundaries consistently.

---

# 9. CONFIRMATION-TIME REVALIDATION

This is mandatory.

When the admin clicks:

**Confirm Booking**

the system must perform a fresh availability check.

Do NOT rely only on the availability shown when the booking request was created.

Example:

Customer A submits request.

Later, another confirmed booking is created manually.

Customer A's old request must not be blindly confirmable.

At confirmation time:

1. Check car global status
2. Check manual availability blocks
3. Check overlapping confirmed bookings
4. If conflict exists:

   * do not confirm
   * display clear error
   * keep request pending
5. If no conflict:

   * confirm booking

The system must prevent overlapping confirmed bookings for the same car.

---

# 10. PENDING REQUESTS

Pending requests are informational requests.

They do not reserve inventory.

Example:

Car:

Swift

Dates:

20–25 September

Request A = PENDING

Request B = PENDING

Both may exist.

If the owner confirms Request A:

Request B must then be checked against the confirmed booking.

Request B cannot subsequently be confirmed if it overlaps.

Admin should visually distinguish:

* PENDING
* CONFIRMED
* MANUAL BLOCK
* REJECTED
* CANCELLED
* COMPLETED

---

# 11. WHATSAPP INTEGRATION

Use WhatsApp deep links only.

Do NOT use the WhatsApp Business API in V1.

Do NOT build server-side automated WhatsApp messaging.

Use:

`https://wa.me/<phone>?text=<encoded_message>`

or the appropriate WhatsApp deep-link format.

The owner's WhatsApp number must come from:

`BusinessSettings`

or an appropriate configurable business contact field.

---

# 12. CUSTOMER WHATSAPP ACTION

Immediately after submitting a booking request, show:

### WhatsApp Owner

The button should open WhatsApp with a pre-filled message containing useful booking information.

Example information:

* Business name
* Customer name
* Booking reference
* Car
* Pickup date/time
* Return date/time
* Pickup location

The message should clearly indicate that the customer is contacting the owner regarding a booking request.

Do NOT write:

“Booking confirmed.”

Instead use wording such as:

“Hi, I submitted a booking request…”

The customer should be encouraged to contact the owner.

---

# 13. OWNER → CUSTOMER WHATSAPP ACTION

After the owner confirms a booking, provide an admin button:

**Confirm & Send WhatsApp**

This does not automatically send a WhatsApp message.

It should generate/open a WhatsApp deep link with a pre-filled confirmation message.

The owner remains responsible for actually sending the message.

The message can contain:

* Business name
* Customer name
* Booking reference
* Car
* Rental dates
* Pickup location
* Confirmed status
* Relevant instructions

Do not expose sensitive information.

---

# 14. PHONE CALL

Provide:

`tel:<phone-number>`

links where appropriate.

Customer should have:

**Call Owner**

buttons on:

* Booking Submitted page
* Contact page
* Relevant booking/admin communication areas where appropriate

Do not claim that the owner will call the customer.

---

# 15. OFFLINE PAYMENTS

V1 must NOT include an online payment gateway.

Do not implement:

* Razorpay
* Stripe
* PayPal
* UPI payment gateway
* Card gateway
* Automated payment confirmation

Payment is handled offline.

The admin should be able to record payment information manually.

Use:

`PaymentRecord`

Fields should support information such as:

* Booking
* Total amount
* Amount paid
* Remaining amount
* Payment status
* Payment method
* Payment date
* Notes
* Created/updated timestamps

Possible payment status:

* UNPAID
* PARTIAL
* PAID
* REFUNDED

Payment methods may include:

* Cash
* UPI
* Bank transfer
* Other

These are records only.

They do not process payments.

---

# 16. SECURITY DEPOSIT

Security deposit is handled offline.

The admin should be able to record:

* Deposit amount
* Deposit status
* Security arrangement
* Date received
* Date returned
* Amount returned
* Notes

Possible security arrangements:

* Cash
* Vehicle/security arrangement
* Other agreed arrangement

Do NOT store unnecessary sensitive government ID information.

Never store complete Aadhaar/passport/license numbers unless there is a legally necessary reason and an explicit future requirement.

Prefer:

* masked reference
* verification status
* document type
* notes

Do not create a public document-upload system in V1.

---

# 17. MULTIPLE PICKUP LOCATIONS

The business may operate from multiple pickup hubs.

Create:

`PickupLocation`

Each location should support:

* Name
* Address
* City
* State
* Postal code
* Google Maps link
* Phone override
* WhatsApp override
* Pickup instructions
* Active/inactive status
* Created/updated timestamps

The booking should store the selected pickup location.

The public website should clearly show available pickup locations.

For V1, prefer storing a Google Maps link and providing:

**Open in Google Maps**

or:

**Get Directions**

Do not unnecessarily introduce the Google Maps API unless the design genuinely requires an embedded map.

---

# 18. CAR DATA MODEL

Create a proper `Car` model.

Recommended fields:

* Brand
* Model
* Display name
* Vehicle class
* Registration number
* Price per day
* Seats
* Fuel type
* Transmission
* Gearbox label
* AC
* Included kilometres
* Description
* Rental rules
* Extra charges
* Global status
* Archived
* Created at
* Updated at

Possible vehicle classes:

* Hatchback
* Sedan
* SUV
* MUV
* Luxury
* Other

Possible fuel:

* Petrol
* Diesel
* CNG
* EV
* Hybrid
* Other

Possible transmission:

* Manual
* Automatic
* AMT
* Other

---

# 19. CAR IMAGES

Create:

`CarImage`

A car can have multiple images.

Support:

* Main image
* Gallery images
* Image ordering
* Active/inactive
* Alt text where useful

Do not permanently depend on local development media files for production.

Production media must be compatible with Cloudinary.

---

# 20. CUSTOMER DATA

Collect only information actually required for the rental workflow.

Customer model should support:

* Name
* Phone
* WhatsApp number if different
* Email if needed
* Basic address if genuinely required
* Notes
* Created at
* Updated at

Do not collect unnecessary sensitive personal data.

Do not expose customer information publicly.

---

# 21. BOOKING MODEL

Create:

`Booking`

Recommended fields:

* Reference code
* Car
* Customer
* Pickup location
* Pickup datetime
* Return datetime
* Message
* Preferred contact method
* Status
* Confirmed at
* Confirmed by
* Created at
* Updated at

Reference codes must be unique and human-friendly.

Example:

`KTF-2026-0001`

or another clean format.

Use a reliable server-side generator.

Do not trust the client to generate booking references.

---

# 22. AVAILABILITY BLOCK MODEL

Create:

`AvailabilityBlock`

Recommended fields:

* Car
* Start datetime
* End datetime
* Reason
* Notes
* Created by
* Created at
* Updated at

Possible reasons:

* OFFLINE_BOOKING
* RESERVED
* MAINTENANCE
* PERSONAL_USE
* UNAVAILABLE
* CLEANING
* OTHER

These blocks must affect public availability.

They are independent from customer booking requests.

---

# 23. BUSINESS SETTINGS

Create:

`BusinessSettings`

Treat it as a singleton/configuration model.

Recommended fields:

* Business name
* Phone
* WhatsApp
* Email
* Currency
* Business hours
* Rental rules
* Default security deposit
* General notes
* Created at
* Updated at

Initial business name:

**Keys to your freedom**

This value must be seeded/configured automatically.

The admin must be able to edit it later.

However, the initial production configuration must remain:

**Keys to your freedom**

unless the project owner explicitly changes it.

---

# 24. ADMIN DASHBOARD

Build a clean owner/admin dashboard.

The admin must be able to manage:

* Cars
* Car images
* Pickup locations
* Availability blocks
* Booking requests
* Customers
* Payments
* Security deposits
* Business settings

Dashboard should show useful summary information such as:

* Pending requests
* Confirmed bookings
* Today's pickups
* Upcoming returns
* Available cars
* Manual blocks
* Payment pending
* Deposit pending

Do not overload the dashboard with unnecessary analytics.

Focus on operational usefulness.

---

# 25. ADMIN BOOKING LIST

Booking list should support:

* Search
* Filter by status
* Filter by car
* Filter by date
* Filter by pickup location
* Sort by newest/upcoming

Display:

* Booking reference
* Customer
* Car
* Pickup
* Return
* Status
* Created date
* Payment status if available

---

# 26. ADMIN BOOKING DETAIL

Booking detail page should show:

### Customer

* Name
* Phone
* WhatsApp
* Email where available

### Booking

* Reference
* Car
* Pickup
* Return
* Pickup location
* Message
* Preferred contact
* Status

### Availability

Show a clear live availability result.

Example:

`AVAILABLE`

or:

`CONFLICT — Cannot confirm`

If conflict exists, explain why.

Possible reasons:

* Existing confirmed booking
* Manual availability block
* Vehicle inactive
* Vehicle under maintenance

Admin actions:

* Confirm
* Reject
* Cancel
* Mark completed
* Record payment
* Record deposit
* Open WhatsApp
* Call customer

---

# 27. ADMIN AVAILABILITY CALENDAR

Create an operational availability calendar.

Support where practical:

* Month view
* Week view
* Timeline-style view

Clearly distinguish:

### CONFIRMED BOOKING

Actual customer reservation.

### PENDING

Customer request only.

Does not block availability.

### MANUAL BLOCK

Owner-controlled unavailable period.

The calendar should make conflicts easy to understand.

Admin should be able to create and remove manual blocks.

---

# 28. PUBLIC WEBSITE

Required public pages:

1. Home
2. Cars
3. Car Details
4. Booking Request
5. Booking Submitted
6. About
7. Contact
8. Rental Rules
9. Privacy

Use Django templates.

Do not introduce React or Next.js unless there is a compelling technical reason approved by the project owner.

---

# 29. HOMEPAGE

Homepage should communicate:

**Keys to your freedom**

as the business identity.

Include:

* Hero section
* Quick search
* Featured cars
* Simple explanation of rental process
* Pickup locations
* Business contact CTA
* Rental benefits/features
* Clear booking/request CTA
* Footer

Quick search can include:

* Pickup date
* Return date
* Pickup location
* Vehicle class
* Gearbox/transmission

Stage 1 may show the visual UI.

Stage 2 must connect search to real availability.

---

# 30. CAR LISTING PAGE

Cars page should show:

* Car image
* Brand/model
* Vehicle class
* Seats
* Fuel
* Transmission
* AC
* Price/day
* Included kilometres
* Availability status where appropriate
* View details button
* Request booking button

Filters should work correctly.

Do not show a car as available if it is actually unavailable for the selected dates.

---

# 31. CAR DETAILS PAGE

Show:

* Image gallery
* Car name
* Price/day
* Seats
* Fuel
* Transmission
* AC
* Included km
* Description
* Rental rules
* Extra charges
* Pickup options
* Selected rental dates
* Booking CTA

Make it obvious that the customer is submitting a request, not automatically confirming a reservation.

---

# 32. BOOKING REQUEST PAGE

Form should collect only necessary information.

Example:

* Name
* Phone
* WhatsApp
* Email
* Pickup location
* Pickup datetime
* Return datetime
* Preferred contact
* Message

Validate:

* Required fields
* Phone format
* Valid dates
* Return after pickup
* Reasonable datetime range
* Car exists
* Pickup location is active

The server must validate everything again.

Never rely only on JavaScript validation.

---

# 33. BOOKING SUBMITTED PAGE

This page is extremely important.

Clearly display:

# Booking Request Received

Then:

**Your booking is NOT confirmed yet.**

Explain:

> Your request has been sent to Keys to your freedom. Please contact the owner on WhatsApp or by phone to discuss and confirm availability.

Display:

* Booking reference
* Car
* Dates
* Pickup location
* Customer name

Primary actions:

### WhatsApp Owner

### Call Owner

Do not imply automatic confirmation.

Do not imply that the owner will contact the customer.

---

# 34. DESIGN SYSTEM

Use the Google Stitch designs as the primary visual reference.

The website should closely reproduce the approved Stitch design language.

Current design direction:

* Light lavender/grey page background
* White cards
* Black/dark primary pills/buttons
* Teal accent
* Red danger states
* Serif/display-style heading font where appropriate
* Clean sans-serif body typography
* Spacious modern layouts
* Rounded cards
* Soft borders
* Clear hierarchy
* Responsive design
* Premium but practical local-business feeling

Do not blindly copy Stitch placeholder content.

Use the Stitch design for:

* Layout
* Spacing
* Typography
* Component hierarchy
* Visual style
* Cards
* Buttons
* Navigation
* Forms
* Responsive behavior

Use this requirements document as the source of truth for:

* Business logic
* Availability
* Booking workflow
* Security
* Data model
* Admin behavior

If Stitch visually conflicts with these business requirements, preserve the business requirements and adapt the UI.

---

# 35. BRANDING RULE

The confirmed brand is:

# Keys to your freedom

Do not write:

* “Your Business Name”
* “Car Rental”
* “Demo Rental”
* “ABC Rentals”
* “Placeholder”
* “Company Name”
* Any invented company name

where the actual business name should appear.

Use:

**Keys to your freedom**

as the actual business brand.

If a shorter display form is visually required, use an appropriate abbreviation only if it remains clearly associated with the official brand.

Do not rename the business.

---

# 36. SHARED TEMPLATE ARCHITECTURE

Use:

`base.html`

for public pages.

Use:

`admin_base.html`

for admin pages.

Create reusable partials/components for:

* Navbar
* Footer
* Buttons
* Cards
* Car cards
* Forms
* Alerts
* Status badges
* Modal/dialogs
* Empty states
* Loading states
* Booking summary
* Admin navigation

Avoid duplicated HTML.

---

# 37. STATIC FILE STRUCTURE

Recommended structure:

```text
car-rental/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── config/
├── cars/
├── bookings/
├── templates/
│   ├── base.html
│   ├── admin_base.html
│   ├── public/
│   ├── bookings/
│   └── admin/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/
```

Keep responsibilities clear.

HTML:

`templates/`

CSS:

`static/css/`

JavaScript:

`static/js/`

Python/Django:

Django app directories.

---

# 38. TECH STACK — FIXED

Use:

### Backend

Python + Django

### Frontend

HTML

CSS

Vanilla JavaScript where required

Django Templates

### Local database

SQLite

### Production database

PostgreSQL through Neon

### Production media

Cloudinary

### Hosting

Render

### Domain/DNS

Cloudflare + custom domain

### Version control

Git + GitHub

Do NOT introduce unnecessary:

* React
* Next.js
* Node backend
* Microservices
* Kubernetes
* GraphQL
* Redis
* Celery
* Docker

unless there is a genuine requirement and the project owner explicitly approves it.

---

# 39. ENVIRONMENT VARIABLES

Never hardcode:

* Django secret key
* Database password
* Cloudinary credentials
* Production secrets
* API keys

Use `.env`.

`.env` must never be committed to Git.

Provide a safe `.env.example`.

Example categories:

```text
SECRET_KEY=
DEBUG=
DATABASE_URL=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

Never place real credentials in source code.

---

# 40. SECURITY

Implement proper Django security practices.

At minimum:

* CSRF protection
* Django authentication
* Secure password handling
* Permission checks
* Server-side validation
* ORM queries
* No raw SQL unless necessary
* XSS-safe template rendering
* Secure session configuration in production
* Environment secrets
* No sensitive data in URLs
* No public access to admin pages
* Admin-only business actions
* Proper access control
* Production HTTPS
* Secure cookies in production
* Proper error handling

Customers must never access another customer's private booking data.

Admin actions must require authentication.

---

# 41. ADMIN AUTHENTICATION

Use Django authentication.

Admin/business dashboard must not be publicly accessible.

Only authenticated authorized users can:

* Confirm bookings
* Reject bookings
* Cancel bookings
* Create manual availability blocks
* Edit cars
* Edit prices
* Edit business settings
* Record payments
* Record deposits
* Manage customers

Do not create a complicated custom authentication system unless required.

---

# 42. DATA INTEGRITY

Use Django ORM and database constraints where appropriate.

Important requirements:

* Unique booking reference
* Valid date ranges
* Valid car relationships
* Valid customer relationships
* Valid pickup locations
* Proper status choices
* Timestamps
* Referential integrity

Prevent accidental deletion of important historical booking records where possible.

Prefer archive/deactivate behavior for cars instead of destructive deletion when historical data depends on them.

---

# 43. UI STATES

Every important UI must handle:

* Loading
* Empty
* Success
* Error
* Validation error
* Disabled
* Conflict
* Unavailable
* Pending
* Confirmed
* Cancelled
* Rejected

Do not leave empty grey Stitch placeholder boxes in the final implementation.

If Stitch contains placeholder blocks, replace them with meaningful real content.

---

# 44. MOBILE RESPONSIVENESS

The website must work properly on:

* Desktop
* Laptop
* Tablet
* Mobile

Prioritize mobile usability.

Check:

* Navigation
* Car cards
* Booking forms
* Date inputs
* Buttons
* WhatsApp CTA
* Call CTA
* Admin dashboard
* Availability calendar

Do not allow important buttons to become unusably small on mobile.

---

# 45. STAGE-BY-STAGE EXECUTION

You must build this project in stages.

Do NOT attempt to build everything at once.

After each stage:

1. Implement the stage
2. Run checks/tests
3. Fix known errors
4. Explain what changed
5. List important files changed
6. Explain how to manually test
7. Suggest Git commit message
8. STOP

Do not automatically continue to the next stage.

Wait for the project owner to explicitly say:

**Proceed to Stage N**

before starting the next stage.

---

# 46. STAGE 1 — FOUNDATION + UI SHELL

Implement:

* Django project scaffolding
* App structure
* Git initialization if required
* requirements.txt
* `.env.example`
* `.gitignore`
* Base templates
* Public layout
* Admin layout shell
* Static CSS
* Static JS
* Responsive navigation
* Footer
* Homepage
* Cars page UI
* Car detail UI
* Booking form UI
* Booking submitted UI
* About
* Contact
* Rental rules
* Privacy
* Admin login shell
* Admin dashboard shell
* SQLite configuration
* Initial BusinessSettings setup

The brand must already be:

**Keys to your freedom**

Do NOT treat it as a placeholder.

Do not implement real booking/availability/payment/deposit logic yet.

Stage 1 goal:

A polished clickable visual website shell.

Test:

* Server runs
* Pages load
* Navigation works
* Responsive layout works
* No major console/server errors
* Branding consistently says “Keys to your freedom”

Then:

* Summarize
* Show changed files
* Explain testing
* Suggest commit
* STOP

---

# 47. STAGE 2 — DATABASE + CARS + AVAILABILITY

Implement:

* Django models
* Migrations
* BusinessSettings
* PickupLocation
* Car
* CarImage
* AvailabilityBlock
* Admin CRUD
* Car management
* Pickup location management
* Manual availability blocks
* Availability calendar
* Public car filtering
* Date filtering
* Vehicle class filtering
* Gearbox/transmission filtering
* Central availability service

Seed:

* Business name = `Keys to your freedom`

Proof test:

1. Create a car
2. Mark it ACTIVE
3. Confirm it appears publicly
4. Create manual block for a date range
5. Search that date range
6. Car disappears from available results
7. Search outside the block
8. Car appears again

Also test:

* Inactive car
* Maintenance car
* Manual block
* Confirmed booking overlap logic if booking model is already staged appropriately
* Pending requests must not be treated as confirmed inventory

Then:

* Test
* Fix errors
* Commit
* STOP

---

# 48. STAGE 3 — BOOKING REQUEST + CUSTOMER CONTACT

Implement:

* Customer model
* Booking model
* Reference generation
* Booking request form
* Server-side validation
* PENDING status
* Booking submitted page
* WhatsApp deep link
* Call link
* Admin booking list
* Admin booking detail
* Live availability check
* Confirm/reject/cancel actions
* Pending overlap warning
* Confirmation-time availability revalidation

Important:

A booking submission creates:

`PENDING`

Never:

`CONFIRMED`

The customer must see:

**Your booking is NOT confirmed yet.**

Test:

1. Customer submits request
2. Booking reference generated
3. Status is PENDING
4. WhatsApp button works
5. Call button works
6. Admin sees request
7. Admin checks availability
8. Admin confirms
9. Car becomes blocked by confirmed booking
10. Another overlapping request cannot be confirmed
11. Manual availability block prevents confirmation
12. Inactive car cannot be confirmed

Then:

* Test
* Fix errors
* Commit
* STOP

---

# 49. STAGE 4 — ADMIN BUSINESS MANAGEMENT

Implement:

* Full dashboard
* Customer management
* PaymentRecord
* SecurityDepositRecord
* Payment tracking
* Deposit tracking
* Confirm & Send WhatsApp action
* BusinessSettings management
* PickupLocation management
* Calendar refinements
* Operational dashboard summaries

Admin should be able to manage the entire business workflow without editing code.

Verify:

`BusinessSettings.business_name`

defaults to:

**Keys to your freedom**

The admin may edit it if the business owner intentionally changes it later.

Do not automatically overwrite the value.

Then:

* Test
* Fix errors
* Commit
* STOP

---

# 50. STAGE 5 — PRODUCTION HARDENING + DEPLOYMENT

Perform complete testing.

Test:

### Customer flow

* Homepage
* Search
* Car listing
* Car details
* Booking request
* Validation
* Pending status
* Booking submitted page
* WhatsApp
* Phone
* Mobile layout

### Admin flow

* Login
* Dashboard
* Cars
* Images
* Availability blocks
* Calendar
* Booking requests
* Booking detail
* Confirm
* Reject
* Cancel
* Complete
* Customers
* Payments
* Deposits
* Business settings
* Pickup locations

### Business logic

Verify:

* PENDING does not block availability
* CONFIRMED blocks availability
* Manual blocks block availability
* INACTIVE cars cannot be booked
* MAINTENANCE cars cannot be booked
* Overlapping confirmed bookings cannot occur
* Confirmation performs live revalidation
* Customer is never falsely told a booking is confirmed
* WhatsApp does not automatically confirm a booking
* Phone link works
* Offline payment works as a record
* Security deposit works as a record

### Branding

Verify that:

**Keys to your freedom**

is consistently used across:

* Navbar
* Homepage
* Footer
* Page titles
* Booking pages
* Contact page
* About page
* Rental rules
* Admin dashboard
* Admin login
* Customer communication
* WhatsApp message templates
* Metadata where appropriate
* Business settings

Do NOT treat the business name as a placeholder.

Do NOT replace it with another business name.

---

# 51. PRODUCTION DEPLOYMENT

Production architecture:

```text
Customer
   ↓
Cloudflare / Custom Domain
   ↓
Render
   ↓
Django Application
   ↓
Neon PostgreSQL
   ↓
Cloudinary Media Storage
```

Use:

### Render

For Django application hosting.

### Neon

For production PostgreSQL.

### Cloudinary

For persistent car images/media.

### Cloudflare

For DNS/custom domain.

The laptop does NOT need to remain switched on after deployment.

---

# 52. PRODUCTION DJANGO SETTINGS

Configure production-safe settings.

At minimum review:

* DEBUG
* SECRET_KEY
* ALLOWED_HOSTS
* CSRF trusted origins
* HTTPS
* Secure cookies
* Static files
* Media files
* Database
* Logging
* Error handling

Do not expose secret values.

---

# 53. DATABASE MIGRATIONS

All Django migrations must be committed to Git.

Before deployment:

* Run migrations
* Verify database schema
* Verify seed/configuration logic
* Verify BusinessSettings
* Verify PickupLocation
* Verify cars

Do not manually modify production database tables without migrations unless absolutely necessary.

---

# 54. MEDIA STORAGE

Local development can use local media.

Production must use Cloudinary or an equivalent persistent storage system.

Do not rely on Render's local filesystem for permanent uploaded car images.

Verify:

* Upload
* Display
* Delete/replace
* Main image
* Gallery images

---

# 55. ERROR HANDLING

Create appropriate:

* 404 page
* 500 page
* Form validation errors
* Availability conflict messages
* Unauthorized/admin access handling

Errors should be user-friendly.

Do not expose:

* Stack traces
* Secret keys
* Database credentials
* Internal paths
* Sensitive implementation details

in production.

---

# 56. PERFORMANCE

Keep the project lightweight.

Use:

* Efficient Django ORM queries
* `select_related`
* `prefetch_related` where useful
* Pagination for large lists
* Optimized images
* Proper static files
* Minimal JavaScript

Do not prematurely optimize.

Correctness comes first.

---

# 57. SEO BASICS

Implement basic SEO structure.

Use meaningful:

* Page titles
* Meta descriptions
* Heading hierarchy
* Image alt text
* URLs
* Open Graph metadata where useful

Business name should be:

**Keys to your freedom**

Do not invent another brand name for SEO.

---

# 58. ACCESSIBILITY

Where practical:

* Semantic HTML
* Labels for forms
* Keyboard-accessible controls
* Visible focus states
* Useful alt text
* Sufficient contrast
* Clear error messages
* Proper button labels

WhatsApp and call buttons must clearly communicate their purpose.

---

# 59. TESTING REQUIREMENT

Do not say something is working without testing it.

At minimum test:

### Automated

* Django system checks
* Model tests
* Availability tests
* Booking tests
* Permission tests
* Form validation tests

### Manual

* Customer booking flow
* Admin confirmation
* Manual car blocking
* Conflict prevention
* WhatsApp link
* Phone link
* Mobile layout

When reporting test results, clearly distinguish:

* Passed
* Failed
* Not tested

Never claim a test passed if it was not actually run.

---

# 60. GIT WORKFLOW

Use Git throughout the project.

Recommended stage commits:

```text
stage 1: foundation and ui shell
stage 2: database cars and availability
stage 3: booking request flow
stage 4: admin business management
stage 5: production hardening and deployment
```

Do not create meaningless commits for every tiny change unless useful.

Before each stage commit:

* Check Git diff
* Check status
* Remove accidental secrets
* Ensure `.env` is ignored
* Ensure migrations are included
* Ensure important files are tracked

---

# 61. DO NOT COMMIT SECRETS

Never commit:

```text
.env
```

or:

* API keys
* Cloudinary secrets
* Database passwords
* Django production secret key
* Private credentials

Use:

`.env.example`

instead.

---

# 62. ANTIGRAVITY IMPLEMENTATION BEHAVIOR

Before changing code:

1. Inspect the existing project.
2. Understand the current structure.
3. Check what is already implemented.
4. Do not blindly overwrite working code.
5. Reuse existing components where appropriate.
6. Follow the Stitch design.
7. Follow this requirements document for business logic.
8. Keep architecture simple.
9. Keep code maintainable.
10. Explain important implementation decisions.

If something already works, do not rewrite it unnecessarily.

---

# 63. IMPORTANT — NEVER VIOLATE THESE RULES

Never:

* Automatically confirm customer bookings
* Treat PENDING as confirmed
* Let customers confirm their own bookings
* Allow overlapping confirmed bookings
* Ignore manual availability blocks
* Depend on owner contacting the customer
* Implement an online payment gateway in V1
* Store unnecessary sensitive government ID information
* Expose customer data publicly
* Hardcode secrets
* Leave Stitch placeholder blocks empty
* Replace “Keys to your freedom” with another business name
* Treat “Keys to your freedom” as a placeholder
* Automatically change the business name
* Move to the next stage without approval

---

# 64. DEFINITION OF DONE

The project is considered complete only when:

### Customer

* Can browse cars
* Can filter cars
* Can select dates
* Can see genuine availability
* Can view car details
* Can submit booking request
* Receives unique booking reference
* Clearly sees booking is NOT confirmed
* Can WhatsApp owner
* Can call owner

### Owner

* Can log in
* Can manage cars
* Can manage car images
* Can create manual availability blocks
* Can view booking requests
* Can view customer details
* Can perform live availability check
* Can confirm/reject/cancel bookings
* Cannot accidentally create overlapping confirmed bookings
* Can manage payments
* Can manage deposits
* Can manage pickup locations
* Can edit business settings

### Business Logic

* PENDING does not block inventory
* CONFIRMED blocks inventory
* Manual blocks block inventory
* Inactive/maintenance cars are unavailable
* Confirmation re-checks availability
* Customer communication is clear
* No false confirmation messages

### Branding

The production website consistently uses:

**Keys to your freedom**

as the configured business name.

The name is stored in:

`BusinessSettings.business_name`

and initially seeded as:

`Keys to your freedom`

### Production

* PostgreSQL works
* Cloudinary works
* Render deployment works
* Cloudflare/custom domain works
* HTTPS works
* Static files work
* Media files work
* Environment variables work
* Production security settings are enabled
* No secrets are committed
* Major tests pass
* Mobile layout works

Only declare the project production-ready if the relevant tests have genuinely passed.

---

# 65. FINAL EXECUTION INSTRUCTION

Start by inspecting the existing project state.

If this is a new project, begin with:

## STAGE 1 — FOUNDATION + UI SHELL

Do not skip ahead.

Do not implement all five stages at once.

Do not ask unnecessary questions if the requirements already provide the answer.

When a reasonable implementation decision is not explicitly specified, choose the simplest production-safe option consistent with this document and explain the decision.

Use:

**Keys to your freedom**

as the confirmed business name from the beginning.

At the end of every stage:

1. Summarize what was implemented.
2. List important files changed.
3. Report tests/checks actually performed.
4. Report any known issues.
5. Provide manual testing instructions.
6. Suggest a Git commit message.
7. STOP.

Wait for the project owner to explicitly say:

**Proceed to Stage 2**

or the relevant next stage before continuing.

---

# END OF MASTER PROMPT
