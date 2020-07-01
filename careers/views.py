from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Job, Applicant, Application
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse


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
    paginate_by = 5


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

    def get_success_url(self):
        return reverse('index')
    
class JobDetailView(generic.DetailView):
    model = Job
    template_name = 'careers/job_detail.html'

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('apply_job', args=[str(kwargs['pk'])]))

class ApplyForJobView(generic.CreateView):
    model = Applicant
    template_name = 'careers/apply.html'
    fields = ['first_name', 'last_name', 'dob', 'email', 'resume']

    def form_valid(self, form):
        # Save the Applicant
        applicant = form.save()

        # Get the job
        job = get_object_or_404(Job, pk=self.kwargs['pk'])

        # Save the Application
        Application.objects.create(job=job, applicant=applicant)

        # Redirect
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('index')