from django.db import models
from administrator.models import Student, Billing
# Create your models here.
class StudentBilling(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)  # Default to False initially
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.student.studentName} - {self.billing.title} - Due: {self.due_date} - Paid: {self.is_paid}"
