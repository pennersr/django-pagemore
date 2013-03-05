def make_aware_utc(dt):
    """
    Kludge to get this working on Django 1.3
    """
    try:
        from django.utils import timezone
        timezone.make_aware(dt, timezone.utc)
    except ImportError:
        return dt
