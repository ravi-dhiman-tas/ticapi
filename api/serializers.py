from rest_framework import serializers, exceptions

from django.contrib.auth.models import User

from api.models import Project, Task
from api.utils import create_username


class AuthCustomTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class SignupSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        full_name = attrs.get('full_name')
        email = attrs.get('email')
        password = attrs.get('password')

        # Missing required fields
        if not full_name and email and password:
            raise exceptions.ValidationError("All fields are required.")

        # User already exists
        if User.objects.filter(email__iexact=email).exists():
            raise exceptions.ValidationError("Account already exist using this email, Please login!")

        user = User.objects.create_user(create_username(full_name.strip().title()), email, password)
        full_name_list = full_name.split()
        user.first_name = full_name_list[0].strip().title()
        if len(full_name_list) > 1:
            last_data = " ".join(full_name_list[1:])
            user.last_name = last_data.strip().title()
        user.save()
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions')


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('name', 'description',)


class ProjectSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Project
        exclude = ()

    def get_user(self, obj):
        return UserSerializer(obj.user).data


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('name', 'description', 'project')


class TaskEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('name', 'description',)


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    class Meta:
        model = Task
        exclude = ()

    def get_user(self, obj):
        return UserSerializer(obj.user).data

    def get_project(self, obj):
        return ProjectSerializer(obj.project).data
