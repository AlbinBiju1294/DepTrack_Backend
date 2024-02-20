from django.db import models

# Create your models here.

#department model
class DeliveryUnit(models.Model):
    du_name = models.CharField(max_length=20, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.du_name)

