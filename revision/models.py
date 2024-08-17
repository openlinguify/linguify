# linguify/revision/models.py
from django.db import models


class Revision(models.Model):
    activity = models.ForeignKey('platforme.Activity', on_delete=models.CASCADE)
    revision_date = models.DateTimeField(auto_now_add=True)
    vocabulaire = models.ForeignKey('platforme.Vocabulaire',
                                    on_delete=models.CASCADE)  # Importer directement Vocabulaire ici

    def __str__(self):
        return f"Révision de '{self.vocabulaire.word}'"

    class Meta:
        verbose_name = "Révision"
        verbose_name_plural = "Révisions"
