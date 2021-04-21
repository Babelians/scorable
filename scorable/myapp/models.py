from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

class Albam(models.Model):
    artist = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,)
    albam_title = models.CharField(max_length=50)
    art = models.ImageField(upload_to='albam_art/', blank=True, default='albam_art/defo.jpg')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Score(models.Model):
    albam = models.ForeignKey(Albam, on_delete=models.CASCADE,)
    song_name = models.CharField(max_length=50)
    score_art = models.ImageField(upload_to='score_art/', blank=True, default='score_art/defo.png')
    comporser = models.CharField(max_length=50)
    musicfile = models.FileField(upload_to='musicfile/')
    midifile = models.FileField(upload_to='midifile/')
    uploaded_at = models.DateTimeField(auto_now_add=True)