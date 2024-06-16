from django.utils import timezone

def convert_to_local_time(utc_time):
    return utc_time.astimezone(timezone.get_current_timezone())
