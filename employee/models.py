from django.db import models
from delivery_unit.models import DeliveryUnit

# Create your models here.
class Employee(models.Model):
    employee_number = models.CharField(max_length = 20, null = False, blank =False)
    name = models.CharField(max_length = 50, null = False, blank =False, unique = True)
    mail_id = models.EmailField(null = False, blank =False, unique = True)
    designation = models.CharField(max_length = 50, null = True, blank = True)
    du = models.ForeignKey(DeliveryUnit, null=True, blank=True, on_delete= models.SET_NULL)
    profile_pic_path = models.CharField(max_length = 50, null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


