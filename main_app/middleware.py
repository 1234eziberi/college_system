from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect


USER_TYPE_REDIRECTS = {
    "1": "admin_home",           # HOD
    "2": "staff_home",           # Staff
    "3": "student_home",         # Student
    "4": "admin_dashboard",      # Administrator
    "5": "exam_dashboard",       # Examination Officer
    "6": "accountant_dashboard", # Accountant
    "7": "others_dashboard",     # Other
    "8": "registrar_dashboard",  # Registrar
}
class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user

        # Allow requests to login/logout/public URLs without interference
        allowed_paths = [
            reverse('login_page'),
            reverse('user_login'),
            reverse('user_logout'),
        ]

        if not user.is_authenticated:
            if request.path in allowed_paths:
                return None  # Allow unauthenticated access to login/logout
            return redirect(reverse('login_page'))

        # Redirect users if they access unauthorized modules
        if user.user_type == '1' and modulename == 'main_app.student_views':
            return redirect(reverse('admin_home'))
        elif user.user_type == '2' and modulename in ['main_app.student_views', 'main_app.hod_views']:
            return redirect(reverse('staff_home'))
        elif user.user_type == '3' and modulename in ['main_app.hod_views', 'main_app.staff_views']:
            return redirect(reverse('student_home'))
        elif user.user_type not in USER_TYPE_REDIRECTS:
            # Unknown role — log out and redirect to login
            logout(request)
            return redirect(reverse('login_page'))

        return None  # All good, proceed with view
