from django.db import models
from authentication.models import Account

class BaseObject(models.Model):
    title = models.CharField(max_length=300, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    user = models.PositiveIntegerField(null=False, blank=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.title} | {self.user}'
 