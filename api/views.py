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
from django.db.models import Q

from api.models import Project, Task
from api.serializers import (AuthCustomTokenSerializer, UserSerializer, SignupSerializer, ProjectCreateSerializer, ProjectSerializer,
    TaskCreateSerializer, TaskSerializer
)

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
            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "Invalid Credentials"
                }
            }
            return Response(content, status.HTTP_200_OK)

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
                    'code': "FAILURE",
                    'message': "Invalid Credentials"
                }
            }
        return Response(content, status.HTTP_200_OK)


class SignUpViewSet(BaseAPIView):
    api_docs = {
        'post':{
            'fields': [
                {
                    'name': 'full_name',
                    'required': True,
                    'description': 'Full Name of user',
                    'type': 'string'
                },
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
        Signup Endpoint for user to create their User Profile
        """
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
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
        return Response(content, status.HTTP_200_OK)


class ProjectListViewSet(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    api_docs = {
        'get': {
            'fields': [
                {
                    'name': 'q',
                    'required': False,
                    'description': 'query',
                    'type': 'string',
                    'paramType': 'query'
                },
            ]
        },
        'post':{
            'fields': [
                {
                    'name': 'name',
                    'required': True,
                    'description': 'Name of project',
                    'type': 'string'
                },
                {
                    'name': 'description',
                    'required': True,
                    'description': 'Description of project',
                    'type': 'string'
                },
            ]
        }
    }

    def get(self, request):
        """
        Projects Endpoint for user to get all Projects
        """
        query = request.GET.get("q", "")
        projects = Project.objects.filter(user=request.user, delete=False).order_by('-viewed', '-created')
        if query:
            for q in query.split():
                projects = projects.filter(
                    Q(name__icontains=q) | Q(description__icontains=q)
                ).distinct().order_by('-created')
        serializer = ProjectSerializer(projects, many=True, context=self.get_serializer_context())
        content = {
            'status': {
                'isSuccess': True,
                'code': "SUCCESS",
                'message': "Success"
            },
            'projects': serializer.data
        }
        return Response(content, status.HTTP_200_OK)

    def post(self, request):
        """
        Projects Endpoint for user to create their Project
        """
        serializer = ProjectCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = Project.objects.create(
            name=serializer.validated_data['name'],
            project_initial="".join(item[:1].title() for item in serializer.validated_data['name'].split()),
            description=serializer.validated_data['description'],
            user=request.user
        )
        serializer = ProjectSerializer(project, context=self.get_serializer_context())
        content = {
            'status': {
                'isSuccess': True,
                'code': "SUCCESS",
                'message': "Success"
            },
            'project': serializer.data
        }
        return Response(content, status.HTTP_200_OK)


class ProjectDetailViewSet(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    api_docs = {
        'get': {
            'fields': [
                {
                    'name': 'q',
                    'required': False,
                    'description': 'query',
                    'type': 'string',
                    'paramType': 'query'
                },
            ]
        },
        'put':{
            'fields': [
                {
                    'name': 'name',
                    'required': True,
                    'description': 'Name of project',
                    'type': 'string'
                },
                {
                    'name': 'description',
                    'required': True,
                    'description': 'Description of project',
                    'type': 'string'
                },
            ]
        }
    }

    def get(self, request, pk):
        """
        Projects Endpoint for user to get a Project
        """
        try:
            query = request.GET.get("q", "")
            project = Project.objects.get(pk=pk, user=request.user, delete=False)
            project.viewed = project.viewed + 1
            project.save()
            project_serializer = ProjectSerializer(project, context=self.get_serializer_context())
            tasks = project.task_set.filter(delete=False).order_by('-viewed', '-created')
            if query:
                for q in query.split():
                    tasks = tasks.filter(
                        Q(seq__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
                    ).distinct().order_by('-viewed', '-created')
            task_serializer = TaskSerializer(tasks, many=True, context=self.get_serializer_context())
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Success"
                },
                'project': project_serializer.data,
                'tasks': task_serializer.data
            }
            return Response(content, status.HTTP_200_OK)
        except:
            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "Not Found"
                }
            }
            return Response(content, status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Projects Endpoint for user to create their Project
        """
        try:
            project = Project.objects.get(pk=pk, user=request.user)
            serializer = ProjectCreateSerializer(project, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = ProjectSerializer(project, context=self.get_serializer_context())
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Success"
                },
                'project': serializer.data
            }
            return Response(content, status.HTTP_200_OK)
        except:
            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "Not Found"
                }
            }
            return Response(content, status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Projects Endpoint for user to delete their Project
        """
        try:
            project = Project.objects.filter(pk=pk, user=request.user).update(delete=True)
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Success"
                }
            }
            return Response(content, status.HTTP_200_OK)
        except:
            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "Not Found"
                }
            }
            return Response(content, status.HTTP_200_OK)


class TaskCreateViewSet(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    api_docs = {
        'post':{
            'fields': [
                {
                    'name': 'name',
                    'required': True,
                    'description': 'Name of task',
                    'type': 'string'
                },
                {
                    'name': 'project',
                    'required': True,
                    'description': 'project name',
                    'type': 'string'
                },
                {
                    'name': 'description',
                    'required': True,
                    'description': 'Description of task',
                    'type': 'string'
                },
            ]
        }
    }

    def post(self, request):
        """
        Tasks Endpoint for user to create task of a project
        """
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.validated_data['project']
        seq = "{}-{}".format(project.project_initial, project.task_set.all().count()+1)
        task = Task.objects.create(
            seq=seq,
            name=serializer.validated_data['name'],
            project=serializer.validated_data['project'],
            description=serializer.validated_data['description'],
            user=request.user
        )
        serializer = TaskSerializer(task, context=self.get_serializer_context())
        content = {
            'status': {
                'isSuccess': True,
                'code': "SUCCESS",
                'message': "Success"
            },
            'task': serializer.data
        }
        return Response(content, status.HTTP_200_OK)


class TaskDetailViewSet(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    api_docs = {
        'put':{
            'fields': [
                {
                    'name': 'name',
                    'required': True,
                    'description': 'Name of task',
                    'type': 'string'
                },
                {
                    'name': 'description',
                    'required': True,
                    'description': 'Description of task',
                    'type': 'string'
                },
            ]
        }
    }

    def get(self, request, pk):
        """
        Tasks Endpoint for user to get a task of project
        """
        try:
            task = Task.objects.get(pk=pk, user=request.user)
            task.viewed = task.viewed + 1
            task.save()
            serializer = TaskSerializer(task, context=self.get_serializer_context())
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Success"
                },
                'tasks': serializer.data
            }
            return Response(content, status.HTTP_200_OK)
        except:
            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "Not Found"
                }
            }
            return Response(content, status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Tasks Endpoint for user to update a task of project
        """
        try:
            task = Task.objects.get(pk=pk, user=request.user)
            serializer = TaskEditSerializer(task, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = TaskSerializer(task, context=self.get_serializer_context())
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Success"
                },
                'task': serializer.data
            }
            return Response(content, status.HTTP_200_OK)
        except:
            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "Not Found"
                }
            }
            return Response(content, status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Tasks Endpoint for user to delete a task of project
        """
        try:
            task = Task.objects.filter(pk=pk, user=request.user).update(delete=True)
            content = {
                'status': {
                    'isSuccess': True,
                    'code': "SUCCESS",
                    'message': "Success"
                }
            }
            return Response(content, status.HTTP_200_OK)
        except:
            content = {
                'status': {
                    'isSuccess': False,
                    'code': "FAILURE",
                    'message': "Not Found"
                }
            }
            return Response(content, status.HTTP_200_OK)
