from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from Parent.models import BaseObject

import json


class Goal(BaseObject):
    projects = models.JSONField(encoder=json.JSONEncoder, decoder=json.JSONDecoder, default=list, null=True, blank=False)
    courses = models.JSONField(encoder=json.JSONEncoder, decoder=json.JSONDecoder, default=list, null=True, blank=False)
    rewards = models.JSONField(encoder=json.JSONEncoder, decoder=json.JSONDecoder, default=list, null=True, blank=False)
    finish_words = models.TextField(null=True, blank=False, default=None)
    missions = models.JSONField(encoder=json.JSONEncoder, decoder=json.JSONDecoder, default=list)
    goals = models.ManyToManyField('Goal', blank=True)
    done = models.BooleanField(null=False, blank=False, default=False)


