from functools import wraps
from django.shortcuts import redirect

def teacher_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is logged in and belongs to the "teacher" group
        if request.user.is_authenticated and request.user.groups.filter(name='teacher').exists():
            # If the user is an admin, allow access to the view
            return view_func(request, *args, **kwargs)
        
        # If the user is not authenticated or not in the "admin" group, redirect to the login page
        return redirect('login')
    
    return _wrapped_view