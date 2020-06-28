from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.JobListView.as_view(), name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('createjob/', views.CreateJobView.as_view(), name='create_job'),
]
