from django.db import models

# Note: While the assignment focuses on algorithmic processing of JSON payloads,
# defining a model helps with data validation and potential future persistence.

class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    estimated_hours = models.FloatField()
    importance = models.IntegerField(help_text="1-10 scale")
    # Storing dependencies as a simplified JSON list of IDs for this exercise
    # In a real DB relation, this would be a ManyToMany field to 'self'
    dependencies = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return self.title