import logging

# rest framework imports
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from Auth.token import token_encode

# Model Imports
from user.models import User

# Serializers Import
from user.serializers import UserSerializer


logger = logging.getLogger(__name__)


class Register(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        try:
            User.objects.get(email=request.data['email'])
            return Response({'message': 'User already exist with the same email'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            request.data['password'] = make_password(request.data['password'])
            user_srlzer = UserSerializer(data=request.data)
            user_srlzer.is_valid(raise_exception=True)
            user_srlzer.save()
            token = token_encode(user_srlzer.instance)
            return Response({'message': 'user register successfully', 'token': token, 'details': user_srlzer.data},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(e)
            print(e)
            return Response({'message': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Profile(APIView):
    @staticmethod
    def get(request):
        try:
            print(request.user.id)
            user_obj = User.objects.get(id=request.user.id, is_active=True)
            user_srlzer = UserSerializer(user_obj)
            return Response(user_srlzer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def put(request):
        try:
            user_obj = User.objects.get(id=request.user.id, is_active=True)
            user_srlzer = UserSerializer(user_obj, data=request.data, partial=True)
            user_srlzer.is_valid(raise_exception=True)
            user_srlzer.save()
            return Response({'message': 'user updated successfully'}, status=status.HTTP_206_PARTIAL_CONTENT)
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            print(e)
            return Response({'message': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def delete(request):
        try:
            user_obj = User.objects.get(id=request.user.id, is_active=True)
            user_obj.is_active = False
            user_obj.save()
            return Response({'message': 'user deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            print(e)
            return Response({'message': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLogin(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        try:
            user_obj = User.objects.get(email=request.data['email'])
            if user_obj.check_password(request.data['password']):
                token = token_encode(user_obj)
                return Response({'token': token, 'details': UserSerializer(user_obj).data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
