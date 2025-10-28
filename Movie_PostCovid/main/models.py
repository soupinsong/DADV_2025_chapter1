# main/models.py
from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    release_date = models.DateField(null=True, blank=True)
    distributor = models.CharField(max_length=200, blank=True)
    producer = models.CharField(max_length=200, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    kobis_id = models.CharField(max_length=50, blank=True)
    kmdb_id  = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.title

class BoxOfficeMonthly(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='monthly_stats')
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    rank = models.PositiveIntegerField()
    sales = models.BigIntegerField()
    audience = models.BigIntegerField()
    screens = models.IntegerField(null=True, blank=True)
    show_count = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [('movie', 'year', 'month', 'rank')]
        indexes = [models.Index(fields=['year', 'month', 'rank'])]

    def __str__(self):
        return f'{self.year}/{self.month:02d} #{self.rank} - {self.movie.title}'
