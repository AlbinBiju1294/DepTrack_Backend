#deptrack/user/rbac.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self,request,view):
        try:
            user_role = request.user.user_role
            if user_role == 5:
                return True
            else:
                return False
        except Exception as ex:
            return False
        
class IsDuhead(permissions.BasePermission):


    
    def has_permission(self,request,view):

        try:
            user_role = request.user.user_role
            if user_role == 1:
                return True
            else:
                return False
        except Exception as ex:
            return False
        
class IsPm(permissions.BasePermission):
    def has_permission(self,request,view):
        try:
            user_role = request.user.user_role
            if user_role == 2:
                return True
            else:
                return False
        except Exception as ex:
            return False
        
class IsUser(permissions.BasePermission):
    def has_permission(self,request,view):
        try:
            user_role = request.user.user_role
            if user_role == 3:
                return True
            else:
                return False
        except Exception as ex:
            return False
    
class IsHrbp(permissions.BasePermission):
    def has_permission(self,request,view):
        try:
            user_role = request.user.user_role
            if user_role == 4:
                return True
            else:
                return False
        except Exception as ex:
            return False