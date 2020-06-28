from django.db import models
from django.contrib.auth.models import User
from .validators import validate_file_extension
from django.urls import reverse

class Applicant(models.Model):
    first_name = models.CharField(verbose_name='First Name', max_length=50)
    last_name = models.CharField(verbose_name='Last Name', max_length=50)
    dob = models.DateField(verbose_name='Date of Birth', help_text="Provide the date in format yyyy-mm-dd")
    email = models.EmailField(verbose_name='Email Id')
    resume = models.FileField('Upload Resume', upload_to='resume', null=True, validators=[validate_file_extension])

    def __str__(self):
        return self.first_name + ' ' + self.last_name

class Job(models.Model):
    
    class JobStatus(models.TextChoices):
        OPEN = 'OPEN'
        CLOSED = 'CLOSED'
    
    title = models.CharField(max_length=100, verbose_name='Job Title')
    descr = models.TextField(max_length=5000, verbose_name='Job Description')
    pub_date = models.DateTimeField(verbose_name='Date Published', auto_now_add=True)
    status = models.CharField(max_length=10, choices=JobStatus.choices, default=JobStatus.OPEN)
    created_by = models.ForeignKey(User, verbose_name='Created By', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-pub_date']

    def get_absolute_url(self):
        #return reverse('job-detail', args=[str(self.id)])
        return ""