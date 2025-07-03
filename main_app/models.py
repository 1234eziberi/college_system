from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)



class CustomUser(AbstractUser):
    USER_TYPE = (
        ('1', "HOD"),
        ('2', "Staff"),
        ('3', "Student"),
        ('4', "Administrator"),
        ('5', "Examination Officer"),
        ('6', "Accountant"),
        ('7', "Other"),
        ('8', "Registrar"),
    )

    STUDENT_STATUS = (
        ('admission', 'In Admission'),
        ('graduate', 'Graduate'),
        ('archived', 'Archived'),
        ('transfer', 'Transferred'),
    )

    GENDER = [("M", "Male"), ("F", "Female")]

    username = None
    email = models.EmailField(unique=True)
    user_type = models.CharField(default='1', choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=10)
    fcm_token = models.TextField(default="")

    # 🎯 Student Status (only meaningful when user_type = '3')
    status = models.CharField(
        max_length=20,
        choices=STUDENT_STATUS,
        default='admission',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"



class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)


class Department(models.Model):
    dcode = models.CharField(max_length=10, primary_key=True)
    dname = models.CharField(max_length=100)
    doffice = models.CharField(max_length=100)
    dphone = models.CharField(max_length=20)

    
    chair = models.ForeignKey('Staff', null=True, blank=True, on_delete=models.SET_NULL, related_name='chaired_departments')
    cstart_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.dname


class Course(models.Model):
    name = models.CharField(max_length=120)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.department.dname}" if self.department else self.name




class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name



class Staff(models.Model):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, null=True, blank=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.admin.first_name} {self.admin.last_name} "






class Subject(models.Model):
    subject_code = models.CharField(max_length=10, primary_key=True)  # Unique identifier
    name = models.CharField(max_length=120)
    credits = models.PositiveIntegerField()
    semester = models.CharField(max_length=10)  # e.g., "Semester 1"
    year = models.PositiveIntegerField()        # e.g., 1, 2, 3
    level = models.CharField(max_length=50)     # e.g., "Undergraduate", "Diploma"
    grade_point = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # Optional
    days = models.CharField(max_length=100)     # e.g., "Mon, Wed, Fri"
    time = models.CharField(max_length=50)      # e.g., "10:00 AM - 12:00 PM"

    staff = models.ForeignKey('Staff', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject_code} - {self.name}"

class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# class StudentResult(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
#     test = models.FloatField(default=0)
#     exam = models.FloatField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

GRADE_CHOICES = [
    ('A', 'A'), ('B+', 'B+'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('F', 'F')
]

REMARK_CHOICES = [
    ('PASS', 'PASS'),
    ('FAIL', 'FAIL'),
    ('INCOMPLETE', 'INCOMPLETE'),
]

class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)

    total_marks = models.FloatField(blank=True, null=True)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True)
    grade_point = models.FloatField(blank=True, null=True)
    remark = models.CharField(max_length=15, choices=REMARK_CHOICES, blank=True)

    semester = models.CharField(max_length=20)  # e.g., "Semester I"
    academic_year = models.CharField(max_length=9)  # e.g., "2024/2025"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total(self):
        self.total_marks = self.test + self.exam
        return self.total_marks

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.academic_year})"





@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == '1':
            Admin.objects.create(admin=instance)
        elif instance.user_type == '2':
            Staff.objects.create(admin=instance)
        elif instance.user_type == '3':
            Student.objects.create(admin=instance)
        elif instance.user_type == '4':
            Administrator.objects.create(admin=instance)
        elif instance.user_type == '5':
            ExaminationOfficer.objects.create(admin=instance)
        elif instance.user_type == '6':
            Accountant.objects.create(admin=instance)
        elif instance.user_type == '7':
            Other.objects.create(admin=instance)
        elif instance.user_type == '8':
            Registrar.objects.create(admin=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == '1' and hasattr(instance, 'hod'):
        instance.hod.save()
    elif instance.user_type == '2' and hasattr(instance, 'staff'):
        instance.staff.save()
    elif instance.user_type == '3' and hasattr(instance, 'student'):
        instance.student.save()
    elif instance.user_type == '4' and hasattr(instance, 'administrator'):
        instance.administrator.save()
    elif instance.user_type == '5' and hasattr(instance, 'examinationofficer'):
        instance.examinationofficer.save()
    elif instance.user_type == '6' and hasattr(instance, 'accountant'):
        instance.accountant.save()
    elif instance.user_type == '7' and hasattr(instance, 'other'):
        instance.other.save()
    elif instance.user_type == '8' and hasattr(instance, 'registrar'):
        instance.registrar.save()




from django.contrib.auth import get_user_model

User = get_user_model()

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.action_description}"



class StudentInvoice(models.Model):
    PAYMENT_MODES = [
        ('FLEXIBLE', 'Flexible'),
        ('FULL', 'Full'),
        # Add more if needed
    ]

    CURRENCY_CHOICES = [
        ('TZS', 'Tanzanian Shilling'),
        ('USD', 'US Dollar'),
        # Add more if needed
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    invoice_no = models.CharField(max_length=20, unique=True)
    control_number = models.CharField(max_length=20, unique=True)
    bank = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='TZS')
    invoice_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    academic_year = models.CharField(max_length=9)  # e.g. "2023/2024"
    created_at = models.DateTimeField(auto_now_add=True)

    def balance(self):
        return self.invoice_amount - self.paid_amount

    def is_paid(self):
        return self.balance() <= 0

    def __str__(self):
        return f"Invoice {self.invoice_no} for {self.student}"

