from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import logging
from django.contrib.auth import update_session_auth_hash
from .serializers import *
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import UpdateAPIView, RetrieveUpdateAPIView, ListCreateAPIView, GenericAPIView
from .rbac import IsDuhead, IsAdmin, IsHrbp, IsPm, IsUser

# Create your views here.

# User registration view


class UserRegistrationView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                res_data = {"success": True, "message": "Registration Successful, Please Login",
                            "data": {"id": user.id, "username": user.username}}
                return Response(res_data, status=status.HTTP_201_CREATED)
            else:
                err_data = str(serializer.errors)
                res_data = {"success": False, "message": "Something weBnt wrong", "data": {
                    "error": err_data}}
                return Response(res_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            res_data = {"success": False, "message": " Something went wrong !", "data": {
                "error": str(ex)}, }
            return Response(res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
