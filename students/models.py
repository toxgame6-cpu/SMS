<<<<<<< HEAD
=======
 
>>>>>>> e4bbf3dd0fc40e84d27f29d23086c4bd0828fc2a
from django.db import models
from django.conf import settings


class StudentFile(models.Model):
    file_name = models.CharField(max_length=255)
    class_name = models.CharField(max_length=100)
    division = models.CharField(max_length=10)
    year = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)
    section = models.CharField(max_length=50, blank=True, default='')
    excel_file = models.FileField(upload_to='excel_files/')
    total_students = models.IntegerField(default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_files'
    )
    upload_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'student_files'
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['class_name']),
            models.Index(fields=['division']),
            models.Index(fields=['year']),
            models.Index(fields=['academic_year']),
        ]

    def __str__(self):
        return self.file_name


class Student(models.Model):
    STATUS_CHOICES = (
        ('normal', 'Normal'),
        ('marked', 'Edit Marked'),
        ('resolved', 'Resolved'),
    )
<<<<<<< HEAD
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
=======
>>>>>>> e4bbf3dd0fc40e84d27f29d23086c4bd0828fc2a

    file = models.ForeignKey(
        StudentFile,
        on_delete=models.CASCADE,
        related_name='students'
    )
    roll_no = models.CharField(max_length=10)
    prn = models.CharField(max_length=30)
<<<<<<< HEAD
    abc_id = models.CharField(max_length=50, blank=True, default='')
=======
>>>>>>> e4bbf3dd0fc40e84d27f29d23086c4bd0828fc2a
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    parent_name = models.CharField(max_length=255, blank=True, default='')
    parent_phone = models.CharField(max_length=15, blank=True, default='')
<<<<<<< HEAD
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, default='')
    address = models.TextField(blank=True, default='')
    permanent_address = models.TextField(blank=True, default='')
=======
    address = models.TextField(blank=True, default='')
>>>>>>> e4bbf3dd0fc40e84d27f29d23086c4bd0828fc2a
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    class_name = models.CharField(max_length=100)
    division = models.CharField(max_length=10)
    year = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='normal')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        ordering = ['roll_no']
        indexes = [
            models.Index(fields=['file']),
            models.Index(fields=['roll_no']),
            models.Index(fields=['prn']),
            models.Index(fields=['full_name']),
            models.Index(fields=['status']),
        ]
        unique_together = ['file', 'roll_no']

    def __str__(self):
        return f"{self.roll_no} - {self.full_name}"

    @property
    def initials(self):
        if self.full_name:
            parts = self.full_name.strip().split()
            if len(parts) >= 2:
                return (parts[0][0] + parts[-1][0]).upper()
            elif len(parts) == 1:
                return parts[0][0].upper()
        return 'S'