from django.db import models

#Level_choices of the languages

LEVEL_LANGUAGES = [
    ('-A1', '-A1'),
    ('A1', 'A1'),
    ('A2', 'A2'),
    ('B1', 'B1'),
    ('B2', 'B2'),
    ('C1', 'C1'),
    ('C2', 'C2'),
]

TYPE_ACTIVITY = [
    ('Vocabulary', 'Vocabulary'),
    ('Grammar', 'Grammar'),
    ('Listening', 'Listening'),
    ('Speaking', 'Speaking'),
    ('Reading', 'Reading'),
    ('Writing', 'Writing'),
    ('Test', 'Test'),
]

class LearningPath(models,Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Unit(models.Model):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    level = models.CharField(max_length=3, choices=LEVEL_LANGUAGES)

    def __str__(self):
        return f"{self.title} - {self.level}"

class Lesson(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=10, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], default='Easy')
    estimated_duration = models.IntegerField(help_text="In minutes")

    def __str__(self):
        return self.title

class Activity(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100, choices=TYPE_ACTIVITY)
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title} - {self.activity_type}"

class Vocabulary(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'activity_type': 'Vocabulary'})
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    example_sentence = models.TextField()

    def __str__(self):
        return self.word

class Grammar(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'activity_type': 'Grammar'})
    title = models.CharField(max_length=100)
    description = models.TextField()
    example = models.TextField()

    def __str__(self):
        return self.title

class Listening(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'activity_type': 'Listening'})
    title = models.CharField(max_length=100)
    audio = models.FileField(upload_to='listening_audio/')

    def __str__(self):
        return self.title

class Speaking(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'activity_type': 'Speaking'})
    title = models.CharField(max_length=100)
    audio = models.FileField(upload_to='speaking_audio/')

    def __str__(self):
        return self.title

class Reading(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'activity_type': 'Reading'})
    title = models.CharField(max_length=100)
    text = models.TextField()

    def __str__(self):
        return self.title

class Writing(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'activity_type': 'Writing'})
    title = models.CharField(max_length=100)
    text = models.TextField()

    def __str__(self):
        return self.title

class Test(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, limit_choices_to={'activity_type': 'Test'})
    question = models.TextField()
    correct_answer = models.CharField(max_length=100)
    incorrect_answers = models.TextField(help_text="Separate the answers with a comma.")


    def __str__(self):
        return self.question

