from django import forms
from .models import Albam, Score
from accounts.forms import CustomUser

class AlbamForm(forms.ModelForm):
    class Meta:
        model = Albam
        fields = ('albam_title', 'art')

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = ('song_name', 'musicfile', 'midifile', 'score_art')

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('face','username')