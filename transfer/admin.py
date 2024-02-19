from django.contrib import admin

# Register your models here.
from .models import Transfer,TransferDetails


# Register your models here.
admin.site.register(TransferDetails)
admin.site.register(Transfer)