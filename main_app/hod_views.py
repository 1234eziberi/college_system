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


def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    subjects = Subject.objects.all()
    total_subject = subjects.count()
    total_course = Course.objects.all().count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name[:7])
        attendance_list.append(attendance_count)

    # Total Subjects and students in Each Course
    course_all = Course.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for course in course_all:
        subjects = Subject.objects.filter(course_id=course.id).count()
        students = Student.objects.filter(course_id=course.id).count()
        course_name_list.append(course.name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)
    
    subject_all = Subject.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        course = Course.objects.get(id=subject.course.id)
        student_count = Student.objects.filter(course_id=course.id).count()
        subject_list.append(subject.name)
        student_count_list_in_subject.append(student_count)


    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Student.objects.all()
    for student in students:
        
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leave = LeaveReportStudent.objects.filter(student_id=student.id, status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leave+absent)
        student_name_list.append(student.admin.first_name)

    context = {
        'page_title': "Administrative Dashboard",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_course': total_course,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list,
        'student_attendance_present_list': student_attendance_present_list,
        'student_attendance_leave_list': student_attendance_leave_list,
        "student_name_list": student_name_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "student_count_list_in_course": student_count_list_in_course,
        "course_name_list": course_name_list,

    }
    return render(request, 'hod_template/home_content.html', context)


def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Staff'}

    if request.method == 'POST':
        if form.is_valid():
            try:
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                phone_number = form.cleaned_data.get('phone_number')
                email = form.cleaned_data.get('email')
                gender = form.cleaned_data.get('gender')
                password = form.cleaned_data.get('password')
                course = form.cleaned_data.get('course')
                department = form.cleaned_data.get('department')

                # 📷 Handle profile picture
                passport = request.FILES.get('profile_pic')
                passport_url = None
                if passport:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)

                # 👤 Create user
                user = CustomUser.objects.create_user(
                    email=email,
                    password=password,
                    user_type='2',  # Staff
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    phone_number=phone_number,
                    profile_pic=passport_url,
                )

                # 🔁 Update auto-created Staff profile
                staff = user.staff  # Automatically created by signal
                staff.course = course
                staff.department = department
                staff.save()

                messages.success(request, "Successfully added staff.")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, f"Could not add staff: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'hod_template/add_staff_template.html', context)


def add_student(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Add Student'}

    if request.method == 'POST':
        if student_form.is_valid():
            # 1. Extract form data
            first_name = student_form.cleaned_data.get('first_name')
            last_name = student_form.cleaned_data.get('last_name')
            phone_number = student_form.cleaned_data.get('phone_number')
            email = student_form.cleaned_data.get('email')
            gender = student_form.cleaned_data.get('gender')
            password = student_form.cleaned_data.get('password')
            course = student_form.cleaned_data.get('course')
            session = student_form.cleaned_data.get('session')

            # 2. Handle profile picture upload
            passport = request.FILES.get('profile_pic')
            passport_url = None
            if passport:
                fs = FileSystemStorage()
                filename = fs.save(passport.name, passport)
                passport_url = fs.url(filename)

            # 3. Create CustomUser with user_type '3' (Student)
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                user_type='3',
                first_name=first_name,
                last_name=last_name,
                profile_pic=passport_url,
                gender=gender,
                address=address
            )

            # 4. Immediately create corresponding Student profile linked to the user
            Student.objects.create(admin=user, course=course, session=session)

            messages.success(request, "Student added successfully.")
            return redirect(reverse('add_student'))
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'hod_template/add_student_template.html', context)

import logging
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST    

logger = logging.getLogger(__name__)

def is_hod_or_superuser(user):
    return user.is_authenticated and (user.user_type == '1' or user.is_superuser)

@login_required
@user_passes_test(is_hod_or_superuser)
def add_department(request):
    form = DepartmentForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Department'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "✅ Department successfully added.")
                return redirect(reverse('add_department'))
            except Exception as e:
                logger.error(f"Error adding department: {e}")
                messages.error(request, "❌ Could not add department.")
        else:
            messages.error(request, "⚠️ Invalid form. Please correct the errors.")
    return render(request, 'hod_template/add_department_template.html', context)

@login_required
@user_passes_test(is_hod_or_superuser)
def manage_department(request):
    departments = Department.objects.all()
    context = {
        'departments': departments,
        'page_title': 'Manage Departments'
    }
    return render(request, 'hod_template/manage_department.html', context)

@login_required
@user_passes_test(is_hod_or_superuser)
def edit_department(request, dcode):
    department = get_object_or_404(Department, pk=dcode)
    form = DepartmentForm(request.POST or None, instance=department)
    context = {
        'form': form,
        'page_title': 'Edit Department'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "✅ Department updated successfully.")
                return redirect(reverse('manage_department'))
            except Exception as e:
                logger.error(f"Error updating department {dcode}: {e}")
                messages.error(request, "❌ Could not update department.")
        else:
            messages.error(request, "⚠️ Form is invalid.")
    return render(request, 'hod_template/add_department_template.html', context)

@login_required
@user_passes_test(is_hod_or_superuser)
@require_POST
def delete_department(request, dcode):
    department = get_object_or_404(Department, pk=dcode)
    try:
        department.delete()
        messages.success(request, "✅ Department deleted successfully.")
    except Exception as e:
        logger.error(f"Error deleting department {dcode}: {e}")
        messages.error(request, "❌ Could not delete department.")
    return redirect(reverse('manage_department'))

def add_course(request):
    form = CourseForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course()
                course.name = name
                course.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_course'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_course_template.html', context)




@login_required
def add_subject(request):
    form = SubjectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Subject successfully added.")
                return redirect('manage_subject')
            except Exception as e:
                messages.error(request, f"Error adding subject: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
    
    context = {
        'form': form,
        'page_title': 'Add Subject'
    }
    return render(request, 'hod_template/add_subject_template.html', context)


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': 'Manage Staff'
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_student(request):
    students = CustomUser.objects.filter(user_type=3)
    context = {
        'students': students,
        'page_title': 'Manage Students'
    }
    return render(request, "hod_template/manage_student.html", context)


def manage_course(request):
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Manage Courses'
    }
    return render(request, "hod_template/manage_course.html", context)


@login_required
def manage_subject(request):
    subjects = Subject.objects.all()
    context = {
        'subjects': subjects,
        'page_title': 'Manage Subjects'
    }
    return render(request, "hod_template/manage_subject.html", context)


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    form = StaffForm(request.POST or None, instance=staff)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Edit Staff'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            phone_number = form.cleaned_data.get('phone_number')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=staff.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.phone_number = phone_number
                staff.course = course
                user.save()
                staff.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:
        user = CustomUser.objects.get(id=staff_id)
        staff = Staff.objects.get(id=user.id)
        return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        'form': form,
        'student_id': student_id,
        'page_title': 'Edit Student'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            phone_number = form.cleaned_data.get('phone_number')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            session = form.cleaned_data.get('session')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                student.session = session
                user.gender = gender
                user.phone_number = phone_number
                student.course = course
                user.save()
                student.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_student', args=[student_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "hod_template/edit_student_template.html", context)


def edit_course(request, course_id):
    instance = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Edit Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course.objects.get(id=course_id)
                course.name = name
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)


@login_required
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=subject)
    
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Subject successfully updated.")
                return redirect('manage_subject')
            except Exception as e:
                messages.error(request, f"Error updating subject: {e}")
        else:
            messages.error(request, "Please correct the form.")

    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Edit Subject'
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Created")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Manage Sessions'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Edit Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Session Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def student_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStudent.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Student Feedback Messages'
        }
        return render(request, 'hod_template/student_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStudent, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def staff_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Staff Feedback Messages'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Staff'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_student_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Students'
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    subjects = Subject.objects.all()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'View Attendance'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify_staff(request):
    staff = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Send Notifications To Staff",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


def admin_notify_student(request):
    student = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Send Notifications To Students",
        'students': student
    }
    return render(request, "hod_template/student_notification.html", context)


@csrf_exempt
def send_student_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Student, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('student_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': student.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStudent(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('staff_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': staff.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(staff=staff, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff'))


def delete_student(request, student_id):
    student = get_object_or_404(CustomUser, student__id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect(reverse('manage_student'))


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some students are assigned to this course already. Kindly change the affected student course and try again")
    return redirect(reverse('manage_course'))


@login_required
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject deleted successfully!")
    except Exception as e:
        messages.error(request, f"Could not delete subject: {e}")
    return redirect('manage_subject')



def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Session deleted successfully!")
    except Exception:
        messages.error(
            request, "There are students assigned to this session. Please move them to another session.")
    return redirect(reverse('manage_session'))



#My hand made views 

from django.contrib.auth.decorators import login_required, user_passes_test
import logging


logger = logging.getLogger(__name__)

# Only HOD (user_type=1) or superusers can add administrators
def is_hod(user):
    return user.is_superuser or user.user_type == "1"

@login_required
@user_passes_test(is_hod)
def add_administrator(request):
    form = AdministratorForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Administrator'}

    if request.method == 'POST':
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.user_type = 4  # Administrator
                user.set_password(form.cleaned_data['password'])

                # Save the image securely
                if request.FILES.get('profile_pic'):
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage(location='media/profile_pics/')
                    filename = fs.save(profile_pic.name, profile_pic)
                    user.profile_pic = 'profile_pics/' + filename

                user.save()

                messages.success(request, "Administrator successfully added.")
                return redirect(reverse('add_administrator'))

            except Exception as e:
                logger.error(f"Error creating administrator: {e}")
                messages.error(request, f"Could not add administrator: {str(e)}")
        else:
            messages.error(request, "Please correct the highlighted errors.")

    return render(request, 'hod_template/add_administrator_template.html', context)

@login_required
@user_passes_test(is_hod)
def manage_administrator(request):
    admins = CustomUser.objects.filter(user_type=4)
    return render(request, 'hod_template/manage_administrator.html', {
        'admins': admins,
        'page_title': 'Manage Administrators'
    })


@login_required
@user_passes_test(is_hod)
def edit_administrator(request, admin_id):
    admin = get_object_or_404(CustomUser, pk=admin_id, user_type=4)
    form = AdministratorForm(request.POST or None, request.FILES or None, instance=admin)
    context = {
        'form': form,
        'page_title': 'Edit Administrator'
    }

    if request.method == 'POST':
        if form.is_valid():
            try:
                user = form.save(commit=False)

                # Update password only if changed
                if form.cleaned_data['password']:
                    user.set_password(form.cleaned_data['password'])

                # Optional: update profile picture
                if 'profile_pic' in request.FILES:
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage(location='media/profile_pics/')
                    filename = fs.save(profile_pic.name, profile_pic)
                    user.profile_pic = 'profile_pics/' + filename

                user.save()
                messages.success(request, "Administrator updated successfully.")
                return redirect('manage_administrator')
            except Exception as e:
                messages.error(request, f"Could not update: {e}")
        else:
            messages.error(request, "Please correct the errors.")
    return render(request, 'hod_template/edit_administrator_template.html', context)


@login_required
@user_passes_test(is_hod)
def delete_administrator(request, admin_id):
    admin = get_object_or_404(CustomUser, pk=admin_id, user_type=4)
    try:
        admin.delete()
        messages.success(request, "Administrator deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting: {e}")
    return redirect('manage_administrator')



@login_required
@user_passes_test(is_hod)
def add_registrar(request):
    form = RegistrarForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Registrar'}

    if request.method == 'POST':
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.user_type = 8  # Registrar
                user.set_password(form.cleaned_data['password'])

                if request.FILES.get('profile_pic'):
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage(location='media/profile_pics/')
                    filename = fs.save(profile_pic.name, profile_pic)
                    user.profile_pic = 'profile_pics/' + filename

                user.save()
                messages.success(request, "Registrar successfully added.")
                return redirect(reverse('add_registrar'))

            except Exception as e:
                messages.error(request, f"Could not add registrar: {str(e)}")
        else:
            messages.error(request, "Please correct the form.")
    return render(request, 'hod_template/add_registrar_template.html', context)

@login_required
@user_passes_test(is_hod)
def manage_registrar(request):
    registrars = CustomUser.objects.filter(user_type=8)
    return render(request, 'hod_template/manage_registrar.html', {
        'registrars': registrars,
        'page_title': 'Manage Registrars'
    })


@login_required
@user_passes_test(is_hod)
def edit_registrar(request, registrar_id):
    registrar = get_object_or_404(CustomUser, pk=registrar_id, user_type=8)
    form = RegistrarForm(request.POST or None, request.FILES or None, instance=registrar)
    context = {'form': form, 'page_title': 'Edit Registrar'}

    if request.method == 'POST':
        if form.is_valid():
            try:
                user = form.save(commit=False)
                if form.cleaned_data['password']:
                    user.set_password(form.cleaned_data['password'])

                if 'profile_pic' in request.FILES:
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage(location='media/profile_pics/')
                    filename = fs.save(profile_pic.name, profile_pic)
                    user.profile_pic = 'profile_pics/' + filename

                user.save()
                messages.success(request, "Registrar updated successfully.")
                return redirect('manage_registrar')
            except Exception as e:
                messages.error(request, f"Update failed: {str(e)}")
    return render(request, 'hod_template/edit_registrar_template.html', context)


@login_required
@user_passes_test(is_hod)
def delete_registrar(request, registrar_id):
    registrar = get_object_or_404(CustomUser, pk=registrar_id, user_type=8)
    try:
        registrar.delete()
        messages.success(request, "Registrar deleted successfully.")
    except Exception as e:
        messages.error(request, f"Deletion failed: {str(e)}")
    return redirect('manage_registrar')



@login_required
@user_passes_test(is_hod)
def add_exam_officer(request):
    form = ExamOfficerForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Exam Officer'}

    if request.method == 'POST':
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.user_type = 5  # Exam Officer
                user.set_password(form.cleaned_data['password'])

                if request.FILES.get('profile_pic'):
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage(location='media/profile_pics/')
                    filename = fs.save(profile_pic.name, profile_pic)
                    user.profile_pic = 'profile_pics/' + filename

                user.save()
                messages.success(request, "Exam Officer successfully added.")
                return redirect('add_exam_officer')

            except Exception as e:
                messages.error(request, f"Could not add exam officer: {str(e)}")
        else:
            messages.error(request, "Please correct the form.")

    return render(request, 'hod_template/add_exam_officer_template.html', context)

@login_required
@user_passes_test(is_hod)
def manage_exam_officer(request):
    officers = CustomUser.objects.filter(user_type=5)
    return render(request, 'hod_template/manage_exam_officer.html', {
        'officers': officers,
        'page_title': 'Manage Exam Officers'
    })
    

@login_required
@user_passes_test(is_hod)
def edit_exam_officer(request, officer_id):
    officer = get_object_or_404(CustomUser, pk=officer_id, user_type=5)
    form = ExamOfficerForm(request.POST or None, request.FILES or None, instance=officer)
    context = {'form': form, 'page_title': 'Edit Exam Officer'}

    if request.method == 'POST':
        if form.is_valid():
            try:
                user = form.save(commit=False)
                if form.cleaned_data['password']:
                    user.set_password(form.cleaned_data['password'])

                if 'profile_pic' in request.FILES:
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage(location='media/profile_pics/')
                    filename = fs.save(profile_pic.name, profile_pic)
                    user.profile_pic = 'profile_pics/' + filename

                user.save()
                messages.success(request, "Exam Officer updated successfully.")
                return redirect('manage_exam_officer')
            except Exception as e:
                messages.error(request, f"Update failed: {str(e)}")
    return render(request, 'hod_template/edit_exam_officer_template.html', context)



@login_required
@user_passes_test(is_hod)
def delete_exam_officer(request, officer_id):
    officer = get_object_or_404(CustomUser, pk=officer_id, user_type=5)
    try:
        officer.delete()
        messages.success(request, "Exam Officer deleted successfully.")
    except Exception as e:
        messages.error(request, f"Deletion failed: {str(e)}")
    return redirect('manage_exam_officer')

@login_required
@user_passes_test(is_hod)
def add_accountant(request):
    form = AccountantForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Accountant'}

    if request.method == 'POST':
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.user_type = '6'  # Accountant (as string, to match CharField)
                user.set_password(form.cleaned_data['password'])

                if request.FILES.get('profile_pic'):
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage(location='media/profile_pics/')
                    filename = fs.save(profile_pic.name, profile_pic)
                    user.profile_pic = 'profile_pics/' + filename

                user.save()
                messages.success(request, "Accountant successfully added.")
                return redirect('add_accountant')

            except Exception as e:
                messages.error(request, f"Could not add accountant: {str(e)}")
        else:
            messages.error(request, "Please correct the form.")

    return render(request, 'hod_template/add_accountant_template.html', context)


@login_required
@user_passes_test(is_hod)
def manage_accountant(request):
    accountants = CustomUser.objects.filter(user_type='6')
    return render(request, 'hod_template/manage_accountant.html', {
        'accountants': accountants,
        'page_title': 'Manage Accountants'
    })


@login_required
@user_passes_test(is_hod)
def edit_accountant(request, accountant_id):
    accountant = get_object_or_404(CustomUser, pk=accountant_id, user_type='6')
    form = AccountantForm(request.POST or None, request.FILES or None, instance=accountant)
    context = {'form': form, 'page_title': 'Edit Accountant'}

    if request.method == 'POST':
        if form.is_valid():
            try:
                user = form.save(commit=False)
                if form.cleaned_data['password']:
                    user.set_password(form.cleaned_data['password'])

                if 'profile_pic' in request.FILES:
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage(location='media/profile_pics/')
                    filename = fs.save(profile_pic.name, profile_pic)
                    user.profile_pic = 'profile_pics/' + filename

                user.save()
                messages.success(request, "Accountant updated successfully.")
                return redirect('manage_accountant')
            except Exception as e:
                messages.error(request, f"Update failed: {str(e)}")
    return render(request, 'hod_template/edit_accountant_template.html', context)


@login_required
@user_passes_test(is_hod)
def delete_accountant(request, accountant_id):
    accountant = get_object_or_404(CustomUser, pk=accountant_id, user_type='6')
    try:
        accountant.delete()
        messages.success(request, "Accountant deleted successfully.")
    except Exception as e:
        messages.error(request, f"Deletion failed: {str(e)}")
    return redirect('manage_accountant')


@login_required
@user_passes_test(is_hod)
def add_other(request):
    form = OtherForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Other User'}

    if request.method == 'POST':
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.user_type = '7'  # Other
                user.set_password(form.cleaned_data['password'])

                if request.FILES.get('profile_pic'):
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage(location='media/profile_pics/')
                    filename = fs.save(profile_pic.name, profile_pic)
                    user.profile_pic = 'profile_pics/' + filename

                user.save()
                messages.success(request, "User successfully added.")
                return redirect('add_other')

            except Exception as e:
                messages.error(request, f"Could not add user: {str(e)}")
        else:
            messages.error(request, "Please correct the form.")

    return render(request, 'hod_template/add_other_template.html', context)


@login_required
@user_passes_test(is_hod)
def manage_other(request):
    others = CustomUser.objects.filter(user_type='7')
    return render(request, 'hod_template/manage_other.html', {
        'others': others,
        'page_title': 'Manage Other Users'
    })


@login_required
@user_passes_test(is_hod)
def edit_other(request, other_id):
    other = get_object_or_404(CustomUser, pk=other_id, user_type='7')
    form = OtherForm(request.POST or None, request.FILES or None, instance=other)
    context = {'form': form, 'page_title': 'Edit Other User'}

    if request.method == 'POST':
        if form.is_valid():
            try:
                user = form.save(commit=False)
                if form.cleaned_data['password']:
                    user.set_password(form.cleaned_data['password'])

                if 'profile_pic' in request.FILES:
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage(location='media/profile_pics/')
                    filename = fs.save(profile_pic.name, profile_pic)
                    user.profile_pic = 'profile_pics/' + filename

                user.save()
                messages.success(request, "User updated successfully.")
                return redirect('manage_other')
            except Exception as e:
                messages.error(request, f"Update failed: {str(e)}")
    return render(request, 'hod_template/edit_other_template.html', context)


@login_required
@user_passes_test(is_hod)
def delete_other(request, other_id):
    other = get_object_or_404(CustomUser, pk=other_id, user_type='7')
    try:
        other.delete()
        messages.success(request, "User deleted successfully.")
    except Exception as e:
        messages.error(request, f"Deletion failed: {str(e)}")
    return redirect('manage_other')

