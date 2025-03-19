from django.db import models
from Parent.models import BaseObject

STATUS_CHOICES = [
    ('in progress', 'in progress'),
    ('completed', 'completed')
]

class Project(BaseObject):
    start_date = models.DateField(null=True, default=None)
    finish_date = models.DateField(null=True, default=None)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0], null=False)

    def __str__(self):
        return f'{self.title} | {self.user}'


class Partition(models.Model):
    title = models.CharField(max_length=70, null=False, blank=False)
    description = models.TextField(null=True, blank=True, default=None)
    done = models.BooleanField(null=False, blank=False, default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} | {self.project.title}'
    
