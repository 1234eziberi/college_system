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

from django.contrib.auth.decorators import login_required, user_passes_test
import logging

from .forms import *
from .models import *

@login_required(login_url='login_page')
def exam_dashboard(request):
    # Restrict only to users with user_type == 5 (Examination Officer)
    if request.user.user_type != '5':
        return redirect('login_page')  # Or raise 403 Forbidden if preferred

    context = {
        'page_title': 'Examination Officer Dashboard',
        'total_students': Student.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_courses': Course.objects.count(),
        # 'total_results_uploaded': ActivityLog.objects.filter(action_description__icontains='result').count(),

        

        'recent_activities': ActivityLog.objects.all().order_by('-timestamp')[:5],
    }
    return render(request, 'exam_officer/exam_dashboard.html', context)