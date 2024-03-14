#deptrack/user/serializers.py

from rest_framework import serializers
from .models import User
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password','email', 'user_role', 'username', 'employee_id')
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

class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email','user_role','status','is_deleted','created_at','employee_id')

class UserProfileSerializerTwo(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','username', 'email','user_role')

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if user:
            return user.email
        else:
            raise serializers.ValidationError("User not found with this email.")
