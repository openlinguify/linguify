from django.db import models

# Create your models here.
NUM_BOXES = 5
BOXES = range(1, NUM_BOXES + 1)

class Card(models.Model):
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    box = models.IntegerField(
        choices=zip(BOXES, BOXES),
        default=BOXES[0],
    )
    date_created = models.DateTimeField(auto_now_add=True)
    last_studied = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question} - {self.answer} - {self.box} - {self.date_created} - {self.last_studied}"
