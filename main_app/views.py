import json
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt

from .EmailBackend import EmailBackend
from .models import Attendance, Session, Subject



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

def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h4>Access Denied</h4>", status=405)

    email = request.POST.get("email", "").strip()
    password = request.POST.get("password", "")

    if not email or not password:
        messages.error(request, "Both email and password are required.")
        return redirect("login_page")

    user = authenticate(request, email=email, password=password)


    if user is None:
        messages.error(request, "Invalid credentials. Please try again.")
        return redirect("login_page")

    if not user.is_active:
        messages.error(request, "Your account is inactive. Contact admin.")
        return redirect("login_page")

    login(request, user)
    redirect_url_name = USER_TYPE_REDIRECTS.get(user.user_type)

    if redirect_url_name:
        return redirect(reverse(redirect_url_name))
    else:
        logout(request)
        messages.error(request, "Your role is not recognized.")
        return redirect("login_page")

    
def login_page(request):
    if request.user.is_authenticated:
        redirect_url = USER_TYPE_REDIRECTS.get(request.user.user_type, "student_home")
        return redirect(reverse(redirect_url))
    return render(request, "main_app/login.html")


def logout_user(request):
    if request.user != None:
        logout(request)
    return redirect("/")


@csrf_exempt
def get_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = Attendance.objects.filter(subject=subject, session=session)
        attendance_list = []
        for attd in attendance:
            data = {
                    "id": attd.id,
                    "attendance_date": str(attd.date),
                    "session": attd.session.id
                    }
            attendance_list.append(data)
        return JsonResponse(json.dumps(attendance_list), safe=False)
    except Exception as e:
        return None


def showFirebaseJS(request):
    data = """
    // Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
firebase.initializeApp({
    apiKey: "AIzaSyBarDWWHTfTMSrtc5Lj3Cdw5dEvjAkFwtM",
    authDomain: "sms-with-django.firebaseapp.com",
    databaseURL: "https://sms-with-django.firebaseio.com",
    projectId: "sms-with-django",
    storageBucket: "sms-with-django.appspot.com",
    messagingSenderId: "945324593139",
    appId: "1:945324593139:web:03fa99a8854bbd38420c86",
    measurementId: "G-2F2RXTL9GT"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
    const notification = JSON.parse(payload);
    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    }
    return self.registration.showNotification(payload.notification.title, notificationOption);
});
    """
    return HttpResponse(data, content_type='application/javascript')
