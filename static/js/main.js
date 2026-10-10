/**
 * Keys to your freedom - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
  // Mobile drawer toggle & overlay
  const mobileToggle = document.getElementById('mobileToggle');
  const mobileDrawer = document.getElementById('mobileDrawer');
  const mobileDrawerOverlay = document.getElementById('mobileDrawerOverlay');

  function openMobileDrawer() {
    if (!mobileDrawer) return;
    mobileDrawer.classList.add('open');
    if (mobileDrawerOverlay) mobileDrawerOverlay.classList.add('open');
    if (mobileToggle) mobileToggle.setAttribute('aria-expanded', 'true');
    document.body.classList.add('drawer-open');
  }

  function closeMobileDrawer() {
    if (!mobileDrawer) return;
    mobileDrawer.classList.remove('open');
    if (mobileDrawerOverlay) mobileDrawerOverlay.classList.remove('open');
    if (mobileToggle) mobileToggle.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('drawer-open');
  }

  if (mobileToggle && mobileDrawer) {
    mobileToggle.addEventListener('click', function (e) {
      e.stopPropagation();
      if (mobileDrawer.classList.contains('open')) {
        closeMobileDrawer();
      } else {
        openMobileDrawer();
      }
    });

    if (mobileDrawerOverlay) {
      mobileDrawerOverlay.addEventListener('click', closeMobileDrawer);
    }

    // Close when clicking any nav link
    mobileDrawer.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', closeMobileDrawer);
    });

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mobileDrawer.classList.contains('open')) {
        closeMobileDrawer();
      }
    });
  }

  // Same as Mobile Checkbox sync in Booking Form
  const sameAsMobileCheckbox = document.getElementById('sameAsMobile');
  const mobileInput = document.getElementById('customerMobile');
  const whatsappInput = document.getElementById('customerWhatsapp');

  if (sameAsMobileCheckbox && mobileInput && whatsappInput) {
    sameAsMobileCheckbox.addEventListener('change', function () {
      if (this.checked) {
        whatsappInput.value = mobileInput.value;
        whatsappInput.readOnly = true;
        whatsappInput.style.opacity = '0.75';
      } else {
        whatsappInput.readOnly = false;
        whatsappInput.style.opacity = '1';
      }
    });

    mobileInput.addEventListener('input', function () {
      if (sameAsMobileCheckbox.checked) {
        whatsappInput.value = this.value;
      }
    });
  }

  // Policy acceptance checkbox gate
  const policyCheckbox = document.getElementById('policyAcceptance');
  const submitBookingBtn = document.getElementById('submitBookingBtn');

  if (policyCheckbox && submitBookingBtn) {
    function updateSubmitState() {
      if (policyCheckbox.checked) {
        submitBookingBtn.disabled = false;
        submitBookingBtn.style.opacity = '1';
        submitBookingBtn.style.cursor = 'pointer';
      } else {
        submitBookingBtn.disabled = true;
        submitBookingBtn.style.opacity = '0.5';
        submitBookingBtn.style.cursor = 'not-allowed';
      }
    }

    policyCheckbox.addEventListener('change', updateSubmitState);
    updateSubmitState(); // Initial check
  }

  // Date range calculator helper
  const pickupDateInput = document.getElementById('pickupDate');
  const returnDateInput = document.getElementById('returnDate');
  const rentalDaysDisplay = document.getElementById('rentalDaysCount');
  const estimatedTotalDisplay = document.getElementById('estimatedTotalAmount');

  function calculateDaysAndPrice() {
    if (!pickupDateInput || !returnDateInput) return;
    const start = new Date(pickupDateInput.value);
    const end = new Date(returnDateInput.value);

    if (start && end && end > start) {
      const diffTime = Math.abs(end - start);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      if (rentalDaysDisplay) {
        rentalDaysDisplay.textContent = `${diffDays} Day${diffDays > 1 ? 's' : ''}`;
      }
      const pricePerDay = parseFloat(pickupDateInput.dataset.pricePerDay || 0);
      if (estimatedTotalDisplay && pricePerDay > 0) {
        estimatedTotalDisplay.textContent = `₹${(diffDays * pricePerDay).toLocaleString('en-IN')}`;
      }
    }
  }

  if (pickupDateInput && returnDateInput) {
    pickupDateInput.addEventListener('change', calculateDaysAndPrice);
    returnDateInput.addEventListener('change', calculateDaysAndPrice);
  }
});
