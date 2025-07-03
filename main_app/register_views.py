from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.utils.timezone import now, timedelta
from django.db.models import Count, Q
from django.contrib.humanize.templatetags.humanize import intcomma
from .models import *
from .forms import *

def is_registrar(user):
    return user.is_authenticated and user.user_type == '8'

@login_required
@user_passes_test(is_registrar)
def registrar_dashboard(request):
    page_title = "Registrar Dashboard"

    # Student Categories
    total_students = Student.objects.count()
    admission_students = Student.objects.filter(admin__status='admission').count()
    graduates = Student.objects.filter(admin__status='graduate').count()
    archived_students = Student.objects.filter(admin__status='archived').count()
    transfer_students = Student.objects.filter(admin__status='transfer').count()

    # Other academic data
    total_courses = Course.objects.count()
    total_subjects = Subject.objects.count()

    # Placeholder logic for uploaded results (you can replace it with actual query)
    total_results_uploaded = Student.objects.filter(studentresult__isnull=False).distinct().count()

    # Recent activities (last 7 days)
    recent_activities = ActivityLog.objects.filter(timestamp__gte=now() - timedelta(days=7)).order_by('-timestamp')[:10]

    context = {
        "page_title": page_title,
        "total_students": total_students,
        "admission_students": admission_students,
        "graduates": graduates,
        "archived_students": archived_students,
        "transfer_students": transfer_students,
        "total_courses": total_courses,
        "total_subjects": total_subjects,
        "total_results_uploaded": total_results_uploaded,
        "recent_activities": recent_activities,
    }

    return render(request, "registrar_template/registrar_dashboard.html", context)
