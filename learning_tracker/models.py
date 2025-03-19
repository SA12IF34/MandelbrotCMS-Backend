from django.db import models
from Parent.models import BaseObject
from django.core.validators import MinValueValidator, MaxValueValidator

SOURCE_CHOICES = [
    ('coursera', 'coursera'),
    ('youtube', 'youtube')
]

STATUS_CHOICES = [
    ('current', 'current'),
    ('later', 'later'),
    ('done', 'done')
]

TYPE_CHOICES = [
    ('list', 'list'),
    ('one', 'one')
]

class Course(BaseObject):
    description = None
    description = models.TextField(null=True, blank=True, default='')
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default=SOURCE_CHOICES[0], null=False, blank=False)
    link = models.TextField(null=False, blank=False)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=STATUS_CHOICES[0], null=False, blank=False)
    image = models.TextField(null=True, blank=False)
    list = models.BooleanField(null=False, blank=False)
    progress = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=False, blank=False, default=0)

class Section(models.Model):
    title = models.CharField(max_length=120, null=False, blank=False)
    done = models.BooleanField(null=False, blank=False, default=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} | {self.course.title}'

 