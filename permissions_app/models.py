 
from django.db import models
from django.conf import settings


class FilePermission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='file_permissions'
    )
    student_file = models.ForeignKey(
        'students.StudentFile',
        on_delete=models.CASCADE,
        related_name='permissions'
    )
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='granted_permissions'
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'file_permissions'
        unique_together = ['user', 'student_file']

    def __str__(self):
        return f"{self.user.full_name} → {self.student_file.file_name}"