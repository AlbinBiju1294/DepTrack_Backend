from django.db import models
from delivery_unit.models import DeliveryUnit

#setting the bands available
class Band():
    band_level = [("A1", "level1"), ("A2", "level2"),
                   ("B1", "level3"), ("B2", "level4"), ("C1", "level5") ]

# Create your models here.
class Employee(models.Model):
    employee_number = models.CharField(max_length = 20, null = False, blank =False)
    name = models.CharField(max_length = 50, null = False, blank =False, unique = True)
    mail_id = models.EmailField(null = False, blank =False, unique = True)
    designation = models.CharField(max_length = 50, null = True, blank = True)
    band = models.CharField(max_length=20,choices=Band.band_level,null=True,blank=True)
    skills = models.CharField(max_length = 200, null = True, blank = True)
    experion_experience = models.FloatField(null = True, blank = True)
    total_experience = models.FloatField(null = True, blank = True)
    du_id = models.ForeignKey(DeliveryUnit, null=True, blank=True, on_delete= models.SET_NULL,db_column='du_id')
    profile_pic_path = models.CharField(max_length = 50, null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    
    
class DeliveryUnitMapping(models.Model):
    du_id = models.ForeignKey(DeliveryUnit,null=True,on_delete= models.SET_NULL,db_column ='du_id')
    du_head_id=models.ForeignKey(Employee,null=True, blank=True,on_delete=models.SET_NULL,related_name="du_head_id",db_column= 'du_head_id')
    hrbp_id=models.ForeignKey(Employee, null=True, blank=True, on_delete= models.SET_NULL,related_name="hrbp_id",db_column= 'hrbp_id')

    def __str__(self):
        return str(self.id)
