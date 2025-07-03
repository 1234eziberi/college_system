import json
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from .forms import *
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

def admin_dashboard(request):
    # Count by roles
    total_staffs = User.objects.filter(user_type='staff').count()
    total_accountants = User.objects.filter(user_type='accountant').count()
    total_students = User.objects.filter(user_type='student').count()
    total_registrars = User.objects.filter(user_type='registrar').count()
    total_examiners = User.objects.filter(user_type='exam_officer').count()
    total_janitors = User.objects.filter(user_type='other').count()

    # Additional stats
    total_courses = Course.objects.count()
    total_subjects = Subject.objects.count()
    # total_results_uploaded = Result.objects.count()

    # Recent logs / actions
    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]

    context = {
        'page_title': "Administrator Dashboard",
        'total_staffs': total_staffs,
        'total_accountants': total_accountants,
        'total_students': total_students,
        'total_registrars': total_registrars,
        'total_examiners': total_examiners,
        'total_janitors': total_janitors,
        'total_courses': total_courses,
        'total_subjects': total_subjects,
        # 'total_results_uploaded': total_results_uploaded,
        'recent_activities': recent_activities,
    }
    return render(request, 'administrator/admin_dashboard.html', context)
