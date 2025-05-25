from django.db import models
from Parent.models import BaseObject


def upload_file(instance, filename):
    return f'notes/{instance.user}/{filename}'

kwargs = {
    "on_delete": models.CASCADE,
    "null": True,
    "blank": True,
    "default": None
}

class Note(BaseObject):
    description = None
    title = None
    title = models.CharField(max_length=110, null=True, blank=True, default=None)
    content = models.TextField(null=False, blank=False)
    drawn_content = models.TextField(null=True, blank=True, default=None)
    uploaded_file = models.FileField(upload_to=upload_file, null=True, blank=True, default=None)

    project = models.ForeignKey('sessions_manager.Project', **kwargs)
    learning_material = models.ForeignKey('learning_tracker.Course', **kwargs)
    entertainment_material = models.ForeignKey('entertainment.Entertainment', **kwargs)
    goal = models.ForeignKey('goals.Goal', **kwargs)
    missions_list = models.ForeignKey('missions.List', **kwargs)


    def __str__(self):

        return f'Note {self.id} | User {self.user}'