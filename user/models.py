from django.db import models
from django.contrib.auth.models import AbstractUser
from employee.models import Employee
from django.contrib.auth.models import Group, Permission

class UserRole():
    USER_ROLES = [(1, "duhead"), (2, "pm"),
                   (3, "user"), (4, "hrbp"), (5,"admin")]


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(blank=True, max_length=254, verbose_name="email address", unique=True)
    user_role = models.IntegerField(null=True, choices=UserRole.USER_ROLES)
    status = models.BooleanField(default=True) 
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    employee_id = models.ForeignKey(Employee, null=True, blank=True, on_delete= models.SET_NULL)
    groups = models.ManyToManyField(Group, blank=True, related_name="custom_users_groups")
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name="custom_users_permissions")

    def __str__(self):
        return str(self.username)
