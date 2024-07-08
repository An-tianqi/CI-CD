from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tickets = models.IntegerField(default=5)

    def __str__(self):
        return self.user.username

class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ville = models.CharField(max_length=100)
    magasin = models.CharField(max_length=100)
    nb_ticket_en_cours = models.IntegerField()
    type_scrap = models.CharField(max_length=50)
    date_scrap = models.DateTimeField(auto_now_add=True)
