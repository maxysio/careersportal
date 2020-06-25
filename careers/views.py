from django.shortcuts import render
from django.views import generic
from .models import Job, Applicant

# Create your views here.
def index(request):
    
    # Get all Jobs in this site
    jobs_num = Job.objects.all().count()

    context = {
        'jobs_num': jobs_num,
    }

    return render(request, 'index.html', context=context)

class JobListView(generic.ListView):
    model = Job
    context_object_name = 'job_list'
    queryset = Job.objects.order_by('-pub_date')
    template_name = 'careers/index.html'