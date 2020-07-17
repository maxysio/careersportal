from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Job, Applicant, Application, JobAnalysis, ApplicantAnalysis
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from decimal import *

import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, EmotionOptions, SentimentOptions, CategoriesOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException

from django.template.defaulttags import register

from pdfminer.high_level import extract_text
import docx2txt

from fuzzywuzzy import process


# Create your views here.
def index(request):
    
    # Get all Jobs in this site
    jobs_num = Job.objects.all().count()

    context = {
        'jobs_num': jobs_num,
    }

    return render(request, 'index.html', context=context)

def analyze_view(request, pk):
    
    ja = GetJobAnalysis(pk, True)

    context = {
        'ja': ja
    }

    return render(request, 'careers/analyzejob.html', context=context)

class ApplicationListView(generic.ListView):
    model = Application
    template_name = 'careers/applications.html'
    context_object_name = 'applications'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(ApplicationListView, self).get_context_data(**kwargs)
        job = get_object_or_404(Job, pk=self.kwargs['pk'])
        
        context['applicant_count'] = Application.objects.filter(job=job).count()
        context['applicants'] = Application.objects.filter(job=job)

        return context

class JobListView(generic.ListView):
    model = Job
    context_object_name = 'job_list'
    template_name = 'careers/index.html'
    paginate_by = 5

    def get_queryset(self):
        return Job.objects.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super(JobListView, self).get_context_data(**kwargs)
        context['app_list'] = Application.objects.all()
        return context

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
        if request.POST.get("Apply"):
            return HttpResponseRedirect(reverse('apply_job', args=[str(kwargs['pk'])]))
        elif request.POST.get("Analyze"):
            return HttpResponseRedirect(reverse('analyze_job', args=[str(kwargs['pk'])]))
        elif request.POST.get("Applicants"):
            return HttpResponseRedirect(reverse('applicants', args=[str(kwargs['pk'])]))

class ApplicantDetailView(LoginRequiredMixin, generic.DetailView):
    model = Applicant
    template_name = 'careers/applicant_detail.html'
    login_url = "login"
    
    def get_context_data(self, **kwargs):
        context = super(ApplicantDetailView, self).get_context_data(**kwargs)
        context['applicant_analysis'] = GetApplicantAnalysis(str(self.kwargs['pk']))
        return context
    
class ApplyForJobView(generic.CreateView):
    model = Applicant
    template_name = 'careers/apply.html'
    fields = ['first_name', 'last_name', 'dob', 'email', 'resume']

    def form_valid(self, form):
        # Save the Applicant
        applicant = form.save()

        # Get the job
        job = get_object_or_404(Job, pk=self.kwargs['pk'])

        # Get Applicant Score
        appl_score = GetApplicantScore(applicant, job)

        # Save the Application
        Application.objects.create(job=job, applicant=applicant, score=appl_score)

        # Redirect
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('index')

def GetApplicantScore(applicant, job):
    applicant_keywords = GetKeywordList(GetApplicantAnalysis(applicant.id, False))
    job_keywords = GetKeywordList(GetJobAnalysis(job.id, False))

    score = 0
    for jk in job_keywords:
        # Check if the keyword has a match in the applicants keywords
        # If yes, increase the score and move to the next
        highest = process.extractOne(jk, applicant_keywords)
        if(len(highest)>0 and highest[1]>80):
            score += 1
    return score

def GetApplicantAnalysis(applicant_id, reanalyze=False):
    # Get the applicant
    applicant = get_object_or_404(Applicant, pk=applicant_id)

    # Check if analsysis already exist
    if(reanalyze==False and ApplicantAnalysis.objects.filter(applicant=applicant).count()>0):
        # return the analysis
        return ApplicantAnalysis.objects.filter(applicant=applicant)
    else:
        # Analyze the details and Save it

        # Get the local filename of the resume
        resume_file_path = applicant.resume
        # Read the resume
        text_to_analyze = resume_file_path
        if str(resume_file_path).lower().endswith(".pdf"):
            text_to_analyze = extract_text(resume_file_path)
        elif str(resume_file_path).lower().endswith(".docx"):
            text_to_analyze = docx2txt.process(resume_file_path)
        else:
            return "Invalid File Type"

        dict_object = AnalyzeText(text_to_analyze)

        if('Error' in dict_object):
            return dict_object

        try:
            ApplicantAnalysis.objects.filter(applicant=applicant).delete()
        except:
            # Do nothing
            pass

        # Keywords
        applicant_keywords = []
        for k in dict_object['keywords']:
            ky_word = k['text'].lower()
            rel = round(Decimal(k['relevance']) * 100, 6)
            applicant_keywords.append(ApplicantAnalysis.objects.create(applicant=applicant, keyword=ky_word, relevance=rel))

        # Return the analysis
        return applicant_keywords

def GetJobAnalysis(job_id, reanalyze=False):

    # Get the job
    job = get_object_or_404(Job, pk=job_id)

    # Check if analysis already exist
    if(reanalyze==False and JobAnalysis.objects.filter(job=job).count()>0 ):
        # Get the analysis
        return JobAnalysis.objects.filter(job=job)
    else:
        # Analyze the details and Save it

        text_to_analyze = job.title + '\n' + job.descr
        #text_to_analyze = 'Tony Stark is the Hulk and Bruce Wayne is BATMAN! Superman fears not Banner, but Wayne'

        dict_object = AnalyzeText(text_to_analyze)

        if('Error' in dict_object):
            return dict_object

        try:
            JobAnalysis.objects.filter(job=job).delete()
        except:
            # Do nothing
            pass

        # Keywords
        job_keywords = []
        count = 0
        for k in dict_object['keywords']:
            if count == 10:
                break
            ky_word = k['text'].lower()
            rel = round(Decimal(k['relevance']) * 100, 6)
            job_keywords.append(JobAnalysis.objects.create(job=job, keyword=ky_word, relevance=rel))
            count += 1

        # Return the analysis
        return job_keywords

def AnalyzeText(text_to_analyze):
    
    
    # Get the analysis
    dict_object = {}

    try:
        response = service.analyze(
        text=text_to_analyze,
        features=Features(entities=EntitiesOptions(),
                        keywords=KeywordsOptions(),
                        )).get_result()
        
        return response
    except ApiException as e:
        dict_object["Error"] = e.message
        return dict_object

def GetKeywordList(arr_kw):
    k_list = []
    for k in arr_kw:
        k_list.append(k.keyword)
    return k_list

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def filter_appplicants(applications, job):
    return applications.filter(job=job)