#deptrack/transfer/models.py
from django.db import models
from employee.models import Employee 
from delivery_unit.models import DeliveryUnit



#setting the predefined status codes
class RequestStatus():
    REQUEST_STATUS = [(1, "Initiated_by_PM"), (2, "approved_by_DUHEAD"),
                   (3, "Completed"), (4, "Rejected"), (5, "Cancelled") ]


#table for storing the transfers
class Transfer(models.Model):

    employee = models.ForeignKey(Employee, null=True, on_delete=models.SET_NULL, related_name='employeetransfers')
    currentdu = models.ForeignKey(DeliveryUnit, null=True, on_delete=models.SET_NULL, related_name = 'cdu' )
    targetdu = models.ForeignKey(DeliveryUnit, null=True, on_delete=models.SET_NULL, related_name = 'tdu')
    status = models.IntegerField(choices=RequestStatus.REQUEST_STATUS,default=1)
    rejection_reason = models.TextField(max_length = 200, null = True, blank = True )
    transfer_date = models.DateField(null = True, blank =True)
    new_pm = models.ForeignKey(Employee, null=True,blank=True, on_delete=models.SET_NULL, related_name='pmassigned')
 

    def __str__(self):
        return str(self.id)

#setting the bands available
class Band():
    band_level = [("A1", "level1"), ("A2", "level2"),
                   ("B1", "level3"), ("B2", "level4"), ("C1", "level5") ]
    

#table for storing the transfer details like employee skills
class TransferDetails(models.Model):

    transfer = models.ForeignKey(Transfer,null=True, on_delete=models.SET_NULL,related_name='details')
    employee_band = models.IntegerField(choices=Band.band_level,default=1)
    total_experience = models.IntegerField(null = False, blank = False)
    experion_experience = models.IntegerField(null = False, blank = False)
    employee_skills = models.TextField(max_length = 200, null = True, blank = True )
    upskilling_suggestions = models.TextField(max_length = 200, null = True, blank = True )
    strengths = models.TextField(max_length = 200, null = True, blank = True )
    areas_of_improvement = models.TextField(max_length = 200, null = True, blank = True )
    additional_training_needs = models.TextField(max_length = 200, null = True, blank = True )
    releaseReason = models.TextField(max_length = 200, null = True, blank = True )
 

    def __str__(self):
        return str(self.id)
