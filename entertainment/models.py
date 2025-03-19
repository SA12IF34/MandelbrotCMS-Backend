from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from Parent.models import BaseObject
import json

TYPE_CHOICES = [
    ('anime&manga', 'anime&manga'),
    ('game', 'game'),
    ('shows&movies', 'shows&movies'),
    ('other', 'other')
]

SUBTYPE_CHOICES = [
    ('anime', 'anime'),
    ('manga', 'manga'),
    ('movie', 'movie'),
    ('show', 'show'),
    ('game', 'game')
]

STATUS_CHOICES = [
    ('current', 'current'),
    ('done', 'done'),
    ('future', 'future')
]

def upload_img(self, file):
    return f'entertainment/{self.id}/{file}'

class Entertainment(BaseObject):
    description = None
    description = models.TextField(null=True, blank=False)
    link = models.TextField(null=False, blank=False)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, null=False, blank=False)
    subtype = models.CharField(max_length=10, choices=SUBTYPE_CHOICES, null=True, blank=False, default=None)
    mal_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_CHOICES[0], null=False, blank=False)
    special = models.BooleanField(null=False, blank=False, default=False)
    image = models.TextField(null=True, blank=False)
    image_upload = models.ImageField(upload_to=upload_img, null=True, blank=False, default=None)
    relatives = models.ManyToManyField('Entertainment', blank=True)
    rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], null=True, blank=False, default=None)
    user_rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], null=True, blank=False, default=None)
    genres = models.JSONField(encoder=json.JSONEncoder, decoder=json.JSONDecoder, default=list)
    locked = models.BooleanField(null=False, blank=False, default=False)
    lock_reason = models.IntegerField(null=True, blank=False, default=None) # Goal Id
    release_date = models.DateField(null=True, blank=True, default=None)
 