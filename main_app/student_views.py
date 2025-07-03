import json
import math
from datetime import datetime

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required



from .forms import *
from .models import *

# @login_required
# def student_home(request):
    
   
#     return render(request, 'student_template/home_content.html', context)


@login_required
def student_home(request):
    student = get_object_or_404(Student, admin=request.user)

    # Get invoices for active academic year
    current_academic_year = "2024/2025"  # Optionally load this dynamically
    invoices = StudentInvoice.objects.filter(student=request.user, academic_year=current_academic_year)

    # Determine payment and registration status
    semester1_paid = invoices.filter(description__icontains="Semester I").all()
    semester2_paid = invoices.filter(description__icontains="Semester II").all()

    def is_fully_paid(qs):
        return all(i.is_paid() for i in qs)

    semester1_registered = is_fully_paid(semester1_paid)
    semester2_registered = is_fully_paid(semester2_paid)

    context = {
        'page_title': 'Student Dashboard',
        'student': student,
        'academic_year': current_academic_year,
        'semester1_registered': semester1_registered,
        'semester2_registered': semester2_registered,
        'program': student.course.name if student.course else "N/A",
        'year': "Second Year",  # Replace with dynamic logic if needed
    
    }

    return render(request, 'student_template/home_content.html', context)





# @ csrf_exempt
# def student_view_attendance(request):
#     student = get_object_or_404(Student, admin=request.user)
#     if request.method != 'POST':
#         course = get_object_or_404(Course, id=student.course.id)
#         context = {
#             'subjects': Subject.objects.filter(course=course),
#             'page_title': 'View Attendance'
#         }
#         return render(request, 'student_template/student_view_attendance.html', context)
#     else:
#         subject_id = request.POST.get('subject')
#         start = request.POST.get('start_date')
#         end = request.POST.get('end_date')
#         try:
#             subject = get_object_or_404(Subject, id=subject_id)
#             start_date = datetime.strptime(start, "%Y-%m-%d")
#             end_date = datetime.strptime(end, "%Y-%m-%d")
#             attendance = Attendance.objects.filter(
#                 date__range=(start_date, end_date), subject=subject)
#             attendance_reports = AttendanceReport.objects.filter(
#                 attendance__in=attendance, student=student)
#             json_data = []
#             for report in attendance_reports:
#                 data = {
#                     "date":  str(report.attendance.date),
#                     "status": report.status
#                 }
#                 json_data.append(data)
#             return JsonResponse(json.dumps(json_data), safe=False)
#         except Exception as e:
#             return None


def student_apply_leave(request):
    form = LeaveReportStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStudent.objects.filter(student=student),
        'page_title': 'Apply for leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('student_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_apply_leave.html", context)


def student_feedback(request):
    form = FeedbackStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStudent.objects.filter(student=student),
        'page_title': 'Student Feedback'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Feedback submitted for review")
                return redirect(reverse('student_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_feedback.html", context)


def student_view_profile(request):
    student = get_object_or_404(Student, admin=request.user)
    form = StudentEditForm(request.POST or None, request.FILES or None,
                           instance=student)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = student.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                student.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('student_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "student_template/student_view_profile.html", context)


@csrf_exempt
def student_fcmtoken(request):
    token = request.POST.get('token')
    student_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        student_user.fcm_token = token
        student_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def student_view_notification(request):
    student = get_object_or_404(Student, admin=request.user)
    notifications = NotificationStudent.objects.filter(student=student)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "student_template/student_view_notification.html", context)


def student_view_result(request):
    student = get_object_or_404(Student, admin=request.user)
    results = StudentResult.objects.filter(student=student)
    context = {
        'results': results,
        'page_title': "View Results"
    }
    return render(request, "student_template/student_view_result.html", context)
