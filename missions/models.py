from django.db import models
from Parent.models import BaseObject

class List(BaseObject):
    description = None
    date = models.DateField(null=False, blank=False)
    goal = models.IntegerField(null=True, blank=True, default=None)
    reward = models.IntegerField(null=True, blank=False, default=None)
    done = models.BooleanField(null=False, blank=False, default=False)

STATUS_CHOICES = [
    ('pending', 'pending'),
    ('working', 'working'),
    ('done', 'done')
] 

class Mission(models.Model):
    content = models.CharField(max_length=300, null=False, blank=False)
    project = models.PositiveIntegerField(null=True, blank=True, default=None)
    course = models.PositiveIntegerField(null=True, blank=True, default=None)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    list = models.ForeignKey(List, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.content} | {self.list.title}'