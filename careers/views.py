from django.shortcuts import render
from django.views import generic
from .models import Job, Applicant
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect


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

class CreateJobView(LoginRequiredMixin, generic.CreateView):
    login_url = "login"
    fields = ['title', 'descr']
    model = Job
    template_name = "careers/createjob.html"
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    