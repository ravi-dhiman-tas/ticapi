
from django.conf.urls import url

from api import views as api_views


urlpatterns = [
    url(r'^signup/$', api_views.SignUpViewSet.as_view()),
    url(r'^auth/$', api_views.AuthenticateUserViewSet.as_view()),

    url(r'^projects/$', api_views.ProjectListViewSet.as_view()), # GET to all and POST to create a project
    url(r'^projects/(?P<pk>[0-9]*)/$', api_views.ProjectDetailViewSet.as_view()), # GET to all and POST to create a project

    url(r'^tasks/$', api_views.TaskCreateViewSet.as_view()),  # GET to all and POST to create a Task
    url(r'^tasks/(?P<pk>[0-9]*)/$', api_views.TaskDetailViewSet.as_view()),

    # url(r'^home/$', api_views.HomeViewSet.as_view()),
]
