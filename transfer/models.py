#deptrack/transfer/models.py
from django.db import models
from employee.models import Employee 
from delivery_unit.models import DeliveryUnit

#setting the predefined status codes
class RequestStatus():
    REQUEST_STATUS = [(1, "Transfer Initiated"), (2, "Pending Acceptance"),
                   (3, "Completed"), (4, "Rejected"), (5, "Cancelled") ]


#table for storing the transfers
class Transfer(models.Model):

    employee_id = models.ForeignKey(Employee, null=False, blank=False, on_delete=models.CASCADE,db_column = 'employee_id')
    currentdu_id = models.ForeignKey(DeliveryUnit, null=False, blank=False, on_delete=models.CASCADE, related_name = 'cdu',db_column = 'currentdu_id')
    targetdu_id = models.ForeignKey(DeliveryUnit, null=False, blank=False, on_delete=models.CASCADE, related_name = 'tdu',db_column = 'targetdu_id')
    status = models.IntegerField(choices=RequestStatus.REQUEST_STATUS)
    rejection_reason = models.TextField(max_length = 200, null = True, blank = True )
    transfer_date = models.DateField(null = False, blank =False)
    newpm_id = models.ForeignKey(Employee, null=True, on_delete=models.CASCADE,db_column = 'newpm_id',related_name = 'newpm_id')
    initiated_by = models.ForeignKey(Employee, null=False, blank=False, on_delete=models.CASCADE,db_column = 'initiated_by',related_name = 'initiated_by')

    def __str__(self):
        return str(self.id)
#setting the bands available
class Band():
    band_level = [("A1", "level1"), ("A2", "level2"),
                   ("B1", "level3"), ("B2", "level4"), ("C1", "level5") ]
    

#table for storing the transfer details like employee skills
class TransferDetails(models.Model):

    transfer_id = models.OneToOneField(Transfer,null=False,blank=False,on_delete=models.CASCADE,related_name='details',db_column = 'transfer_id')
    employee_band = models.CharField(max_length=100,choices=Band.band_level)
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
