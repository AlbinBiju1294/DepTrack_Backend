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


#Mapping table for department to department head and hrbp
class DeliveryUnitMapping(models.Model):
    du_id = models.ForeignKey(DeliveryUnit,null=True,on_delete= models.SET_NULL,db_column="db_column")
    du_head_id=models.ForeignKey(Employee,null=True, blank=True,on_delete=models.SET_NULL,related_name="du_head_id",db_column="du_head_id")
    hrbp_id=models.ForeignKey(Employee, null=True, blank=True, on_delete= models.SET_NULL,related_name="hrbp_id",db_column="hrbp_id")
