from rest_framework import serializers
from django.contrib.auth.models import User
from .models import History

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User 
        fields = ['id', 'username', 'password', 'email']

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['user', 'ville', 'magasin', 'nb_ticket_en_cours', 'type_scrap', 'date_scrap']

