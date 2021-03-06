# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(max_length=255)
    project_initial = models.CharField(max_length=255)
    description = models.TextField()
    viewed = models.IntegerField(default=0)
    user = models.ForeignKey(User)
    delete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)


STATUS_CHOICES = (
    (0, 'Pending'),
    (1, 'Progress'),
    (2, 'Done'),
)

class Task(models.Model):
    seq = models.CharField(max_length=255)
    delete = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    description = models.TextField()
    viewed = models.IntegerField(default=0)
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)
