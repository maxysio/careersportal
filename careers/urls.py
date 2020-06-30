from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.JobListView.as_view(), name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('createjob/', views.CreateJobView.as_view(), name='create_job'),
    path('jobs/<int:pk>', views.JobDetailView.as_view(), name='job_detail'),
    path('jobs/<int:pk>/apply', views.ApplyForJobView.as_view(), name='apply_job'),
]
