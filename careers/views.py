from django.shortcuts import render
from .models import Job, Applicant

# Create your views here.
def index(request):
    
    # Get all Jobs in this site
    jobs_num = Job.objects.all().count()

    context = {
        'jobs_num': jobs_num,
    }

    return render(request, 'index.html', context=context)