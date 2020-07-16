from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.JobListView.as_view(), name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('createjob/', views.CreateJobView.as_view(), name='create_job'),
    path('jobs/<int:pk>', views.JobDetailView.as_view(), name='job_detail'),
    path('jobs/<int:pk>/apply', views.ApplyForJobView.as_view(), name='apply_job'),
    path('jobs/<int:pk>/analysis', views.analyze_view, name='analyze_job'),
    path('applicants/<int:pk>', views.ApplicantDetailView.as_view(), name='applicant_detail'),
    path('jobs/<int:pk>/applicants_analysis', views.analyze_applicants, name='applicants_analysis'),
]

