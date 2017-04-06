# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import parsers
from rest_framework import renderers
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_backends
from django.contrib.auth.models import User
from django.conf import settings

from api.serializers import AuthCustomTokenSerializer, UserSerializer


class BaseAPIView(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def get_serializer_context(self):
        return {'request': self.request}


class AuthenticateUserViewSet(BaseAPIView):
    api_docs = {
        'post':{
            'fields': [
                {
                    'name': 'email',
                    'required': True,
                    'description': 'Email of user',
                    'type': 'string'
                },
                {
                    'name': 'password',
                    'required': True,
                    'description': 'Password of user',
                    'type': 'string'
                },
            ]
        }
    }

    def post(self, request):
        """
        Authenticate the user. Requires email and password, returns the User Profile and Authentication Token. Please use 'Token <token> in your Authorization header'.
        """

        serializer = AuthCustomTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user_request = get_object_or_404(User, email__iexact=email)
        except:
            return Response(get_error_data(codes.FAILURE, constants.FAILURE), status.HTTP_400_BAD_REQUEST)

        username = user_request.username
        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user, context=self.get_serializer_context())

            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Success"
                },
                'token': token.key,
                'user': serializer.data
            }
        else:
            content = {
                'status': {
                    'isSuccess': False,
                    'code': code,
                    'message': message
                }
            }

        return Response(content, status.HTTP_200_OK)


