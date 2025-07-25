
from django.urls import path

from main_app.EditResultView import EditResultView

from . import (hod_views, staff_views, student_views, views, administrator_views, exam_views,
others_views, accountant_views, register_views,)

urlpatterns = [
    path("", views.login_page, name='login_page'),

    path("get_attendance", views.get_attendance, name='get_attendance'),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name='showFirebaseJS'),
    path("doLogin/", views.doLogin, name='user_login'),
    path("logout_user/", views.logout_user, name='user_logout'),
    path("admin/home/", hod_views.admin_home, name='admin_home'),
    path("staff/add", hod_views.add_staff, name='add_staff'),
    path("course/add", hod_views.add_course, name='add_course'),
    path("send_student_notification/", hod_views.send_student_notification,
         name='send_student_notification'),
    path("send_staff_notification/", hod_views.send_staff_notification,
         name='send_staff_notification'),
    path("add_session/", hod_views.add_session, name='add_session'),
    path("admin_notify_student", hod_views.admin_notify_student,
         name='admin_notify_student'),
    path("admin_notify_staff", hod_views.admin_notify_staff,
         name='admin_notify_staff'),
    path("admin_view_profile", hod_views.admin_view_profile,
         name='admin_view_profile'),
    path("check_email_availability", hod_views.check_email_availability,
         name="check_email_availability"),
    path("session/manage/", hod_views.manage_session, name='manage_session'),
    path("session/edit/<int:session_id>",
         hod_views.edit_session, name='edit_session'),
    path("student/view/feedback/", hod_views.student_feedback_message,
         name="student_feedback_message",),
    path("staff/view/feedback/", hod_views.staff_feedback_message,
         name="staff_feedback_message",),
    path("student/view/leave/", hod_views.view_student_leave,
         name="view_student_leave",),
    path("staff/view/leave/", hod_views.view_staff_leave, name="view_staff_leave",),
    path("attendance/view/", hod_views.admin_view_attendance,
         name="admin_view_attendance",),
    path("attendance/fetch/", hod_views.get_admin_attendance,
         name='get_admin_attendance'),
    path("student/add/", hod_views.add_student, name='add_student'),
    path("subject/add/", hod_views.add_subject, name='add_subject'),
    path("staff/manage/", hod_views.manage_staff, name='manage_staff'),
    path("student/manage/", hod_views.manage_student, name='manage_student'),
    path("course/manage/", hod_views.manage_course, name='manage_course'),
    path("subject/manage/", hod_views.manage_subject, name='manage_subject'),
    path("staff/edit/<int:staff_id>", hod_views.edit_staff, name='edit_staff'),
    path("staff/delete/<int:staff_id>",
         hod_views.delete_staff, name='delete_staff'),

    path("course/delete/<int:course_id>",
         hod_views.delete_course, name='delete_course'),

    path("subject/delete/<int:subject_id>",
         hod_views.delete_subject, name='delete_subject'),

    path("session/delete/<int:session_id>",
         hod_views.delete_session, name='delete_session'),

    path("student/delete/<int:student_id>",
         hod_views.delete_student, name='delete_student'),
    path("student/edit/<int:student_id>",
         hod_views.edit_student, name='edit_student'),
    path("course/edit/<int:course_id>",
         hod_views.edit_course, name='edit_course'),
    path("subject/edit/<int:subject_id>",
         hod_views.edit_subject, name='edit_subject'),

         #My own handmade urls

    path('add_administrator/', hod_views.add_administrator, name='add_administrator'),
    path('manage_administrator/', hod_views.manage_administrator, name='manage_administrator'),
    path('edit_administrator/<int:admin_id>/', hod_views.edit_administrator, name='edit_administrator'),
    path('delete_administrator/<int:admin_id>/', hod_views.delete_administrator, name='delete_administrator'),

    path('add_registrar/', hod_views.add_registrar, name='add_registrar'),
    path('manage_registrar/', hod_views.manage_registrar, name='manage_registrar'),
    path('edit_registrar/<int:registrar_id>/', hod_views.edit_registrar, name='edit_registrar'),
    path('delete_registrar/<int:registrar_id>/', hod_views.delete_registrar, name='delete_registrar'),

    path('add_exam_officer/', hod_views.add_exam_officer, name='add_exam_officer'),
    path('manage_exam_officer/', hod_views.manage_exam_officer, name='manage_exam_officer'),
    path('edit_exam_officer/<int:officer_id>/', hod_views.edit_exam_officer, name='edit_exam_officer'),
    path('delete_exam_officer/<int:officer_id>/', hod_views.delete_exam_officer, name='delete_exam_officer'),

    path('accountant/add/', hod_views.add_accountant, name='add_accountant'),
    path('accountant/manage/', hod_views.manage_accountant, name='manage_accountant'),
    path('accountant/edit/<int:accountant_id>/', hod_views.edit_accountant, name='edit_accountant'),
    path('accountant/delete/<int:accountant_id>/', hod_views.delete_accountant, name='delete_accountant'),

    # Other user URLs
    path('other/add/', hod_views.add_other, name='add_other'),
    path('other/manage/', hod_views.manage_other, name='manage_other'),
    path('other/edit/<int:other_id>/', hod_views.edit_other, name='edit_other'),
    path('other/delete/<int:other_id>/', hod_views.delete_other, name='delete_other'),

    path('add-department/', hod_views.add_department, name='add_department'),
    path('manage-department/', hod_views.manage_department, name='manage_department'),
    path('edit-department/<str:dcode>/', hod_views.edit_department, name='edit_department'),
    path('delete-department/<str:dcode>/', hod_views.delete_department, name='delete_department'),


     


    # Staff
    path("staff/home/", staff_views.staff_home, name='staff_home'),
    path("staff/apply/leave/", staff_views.staff_apply_leave,
         name='staff_apply_leave'),
    path("staff/feedback/", staff_views.staff_feedback, name='staff_feedback'),
    path("staff/view/profile/", staff_views.staff_view_profile,
         name='staff_view_profile'),
    path("staff/attendance/take/", staff_views.staff_take_attendance,
         name='staff_take_attendance'),
    path("staff/attendance/update/", staff_views.staff_update_attendance,
         name='staff_update_attendance'),
    path("staff/get_students/", staff_views.get_students, name='get_students'),
    path("staff/attendance/fetch/", staff_views.get_student_attendance,
         name='get_student_attendance'),
    path("staff/attendance/save/",
         staff_views.save_attendance, name='save_attendance'),
    path("staff/attendance/update/",
         staff_views.update_attendance, name='update_attendance'),
    path("staff/fcmtoken/", staff_views.staff_fcmtoken, name='staff_fcmtoken'),
    path("staff/view/notification/", staff_views.staff_view_notification,
         name="staff_view_notification"),
    path("staff/result/add/", staff_views.staff_add_result, name='staff_add_result'),
    path("staff/result/edit/", EditResultView.as_view(),
         name='edit_student_result'),
    path('staff/result/fetch/', staff_views.fetch_student_result,
         name='fetch_student_result'),



    # Student
   



    path('student/home/', student_views.student_home, name='student_home'),
    
    path("student/apply/leave/", student_views.student_apply_leave,
         name='student_apply_leave'),
    path("student/feedback/", student_views.student_feedback,
         name='student_feedback'),
    path("student/view/profile/", student_views.student_view_profile,
         name='student_view_profile'),
    path("student/fcmtoken/", student_views.student_fcmtoken,
         name='student_fcmtoken'),
    path("student/view/notification/", student_views.student_view_notification,
         name="student_view_notification"),
    path('student/view/result/', student_views.student_view_result,
         name='student_view_result'),



    ##College Managers /Administarators

    path('admin/dashboard/', administrator_views.admin_dashboard, name='admin_dashboard'),   

    #EXAM OFFICERS
    path('exam/dashboard/', exam_views.exam_dashboard, name='exam_dashboard'),

    #ACCOUNTANT
    path('accountant/dashboard/', accountant_views.accountant_dashboard, name='accountant_dashboard'),

    #OTHER
    path('others/dashboard/', others_views.others_dashboard, name='others_dashboard'),

    #REGISTRAR
    path('registrar/dashboard/', register_views.registrar_dashboard, name='registrar_dashboard'),
  

]
