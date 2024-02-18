#deptrack/user/serializers.py

from rest_framework import serializers
from .models import User
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password', 'email', 'user_role', 'username', 'employee_id')
        extra_kwargs = {
            'username': {'required': True},
            'password': {'write_only': True, 'required': True},
            'email': {'required': False},
            'user_role': {'required': True},
            'employee_id':{'required': True}
        }

    def create(self, validated_data):
            if 'username' not in validated_data:
                raise ValidationError({'username': 'This field is required'})
            return User.objects.create_user(**validated_data)