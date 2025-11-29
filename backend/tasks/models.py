from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    estimated_hours = models.FloatField()
    importance = models.IntegerField(help_text="1-10 scale")
    dependencies = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return self.title