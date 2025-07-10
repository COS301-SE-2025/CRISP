from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer
from auth_api.models import CrispUser
import traceback
import json

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Print request data for debugging
            print(f"Login request data: {request.data}")
            
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            
            if user is None:
                return Response({'detail': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
            
            refresh = RefreshToken.for_user(user)
            
            # Manually create user data to avoid serializer issues
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': getattr(user, 'email', ''),
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
                'role': getattr(user, 'role', ''),
                'organization': getattr(user, 'organization', ''),
                'is_admin': user.is_staff or 
                           (hasattr(user, 'role') and user.role and user.role.lower() in ['admin', 'administrator'])
            }
            
            # Print response data for debugging
            response_data = {
                'user': user_data,
                'token': str(refresh.access_token),
                'refresh': str(refresh)
            }
            print(f"Login response: {json.dumps(response_data)}")
            
            return Response(response_data)
            
        except Exception as e:
            # Print detailed error information
            print(f"Login error: {str(e)}")
            traceback.print_exc()
            return Response({'detail': f'Login error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            
            return Response({
                'user': user_serializer.data,
                'token': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Manually create user data to avoid serializer issues
            user = request.user
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': getattr(user, 'email', ''),
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
                'role': getattr(user, 'role', ''),
                'organization': getattr(user, 'organization', ''),
                'is_admin': user.is_staff or 
                           (hasattr(user, 'role') and user.role and user.role.lower() in ['admin', 'administrator'])
            }
            return Response(user_data)
        except Exception as e:
            print(f"User view error: {str(e)}")
            traceback.print_exc()
            return Response({'detail': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)