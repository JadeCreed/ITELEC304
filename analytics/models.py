from django.db import models


CATEGORY_CHOICES = [
    ('Study', 'Study'),
    ('Social', 'Social'),
    ('Gaming', 'Gaming'),
    ('Work', 'Work'),
    ('Entertainment', 'Entertainment'),
]


class ScreenTimeLog(models.Model):
    app_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    duration_minutes = models.PositiveIntegerField()
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.app_name} ({self.category}) - {self.duration_minutes} min on {self.date}"

    @property
    def get_productivity_impact(self):
        impacts = {
            'Study': 'Positive',
            'Work': 'Positive',
            'Social': 'Negative',
            'Gaming': 'Negative',
            'Entertainment': 'Neutral',
        }
        return impacts.get(self.category, 'Neutral')