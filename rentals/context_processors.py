def business_context(request):
    """
    Global context processor providing business identity information.
    Fallback values are used if BusinessSettings is not yet migrated/configured.
    """
    context = {
        'BUSINESS_NAME': 'Keys to your freedom',
        'BUSINESS_PHONE': '+91 98765 43210',
        'BUSINESS_WHATSAPP': '+919876543210',
        'BUSINESS_EMAIL': 'rentals@keystoyourfreedom.com',
        'BUSINESS_ADDRESS': 'Near Central Airport Terminal, Goa, India',
        'BUSINESS_HOURS': 'Open 24/7 (Mon - Sun)',
        'CURRENCY_SYMBOL': '₹',
    }
    
    # In later parts, if BusinessSettings model is loaded from DB, we override gracefully:
    try:
        from rentals.models import BusinessSettings
        settings = BusinessSettings.objects.first()
        if settings:
            if settings.business_name:
                context['BUSINESS_NAME'] = settings.business_name
            if settings.phone:
                context['BUSINESS_PHONE'] = settings.phone
            if settings.whatsapp:
                context['BUSINESS_WHATSAPP'] = settings.whatsapp
            if settings.email:
                context['BUSINESS_EMAIL'] = settings.email
            if settings.currency:
                context['CURRENCY_SYMBOL'] = settings.currency
    except Exception:
        pass

    return context
