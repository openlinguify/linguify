# revision/models.py
from django.db import models
#from platforme.models import Vocabulaire
from platforme.models import Vocabulaire
from django.utils import timezone

class Revision(models.Model):
    activity = models.ForeignKey('platforme.Activity', on_delete=models.CASCADE)
    vocabulaire = models.ForeignKey('platforme.Vocabulaire', on_delete=models.CASCADE)
    know = models.BooleanField(default=False)
    last_reviewed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Révision de '{self.vocabulaire.word}'"

    class Meta:
        verbose_name = "Révision"
        verbose_name_plural = "Révisions"

