# test_models.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from random import randint
from django.http import HttpResponse
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user_model
import csv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
import json
from selenium.webdriver.firefox.service import Service as FirefoxService
import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer, HistorySerializer
from .models import Profile, History
from django.db import IntegrityError
from rest_framework.permissions import AllowAny

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
import os
import stripe
from unittest.mock import MagicMock, patch
from django.test import RequestFactory
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from back.views import contact

@pytest.fixture
def user():
    # Fixture pour créer un utilisateur de test
    return User.objects.create_user(username='testuser', password='12345', email='testuser@example.com')

@pytest.mark.django_db(transaction=True)
def test_profile_creation(user):
    # Test de création de profil associé à un utilisateur
    profile = Profile.objects.create(user=user, tickets=10)

    # Vérifier que le profil a été créé correctement
    assert profile.user == user
    assert profile.tickets == 10

    # Essayez de créer à nouveau le profil pour le même utilisateur
    with pytest.raises(IntegrityError):
        Profile.objects.create(user=user, tickets=5)



@pytest.mark.django_db
def test_history_creation():
    user = User.objects.create_user(username='yanis2', password='Pass1234!')
    history = History.objects.create(
        user=user,
        ville='Paris',
        magasin='Carrefour',
        nb_ticket_en_cours=3,
        type_scrap='daily'
    )

    assert history.user.username == 'yanis2'
    assert history.ville == 'Paris'
    assert history.magasin == 'Carrefour'
    assert history.nb_ticket_en_cours == 3
    assert history.type_scrap == 'daily'
    assert history.date_scrap is not None

@pytest.fixture
def request_factory():
    return RequestFactory()

@pytest.fixture
def mock_email_backend_send():
    with patch('django.core.mail.backends.smtp.EmailBackend.send') as mock_send:
        yield mock_send


def test_contact_missing_fields(request_factory):
    # Création de la requête simulée sans un des champs requis (name dans ce cas)
    data = {'subject': 'Test Subject', 'message': 'Test Message'}
    request = request_factory.post('/contact/', data)
    request.user = MagicMock(email='john.doe@example.com')

    # Appel de la vue contact
    response = contact(request)

    # Assertions
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['message'] == 'Tous les champs sont requis.'

@pytest.mark.django_db
@patch('stripe.checkout.Session.create')
def test_create_checkout_session(mock_session_create):
    client = APIClient()
    url = reverse('create_checkout_session')  # Assurez-vous que 'create_checkout_session' est bien le nom de votre vue dans les urls

    # Créer un utilisateur pour le test
    user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
    token = Token.objects.create(user=user)

    # Ajouter le token à l'en-tête de la requête
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # Données de test pour la requête POST
    data = {'tickets': 15}  # Choisir un nombre de tickets valide

    # Mock de la réponse de Stripe pour simuler la création de session
    mock_session_create.return_value = MagicMock(id='mock_session_id')

    # Exécuter la requête POST
    response = client.post(url, data, format='json')

    # Vérifier la réponse
    assert response.status_code == status.HTTP_200_OK
    assert 'sessionId' in response.data
    assert response.data['sessionId'] == 'mock_session_id'

    # Vérifier que la méthode de création de session a été appelée avec les bonnes données
    mock_session_create.assert_called_once_with(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': '15 Tickets',
                },
                'unit_amount': 1499,  # Assurez-vous que les montants sont corrects selon votre logique
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:3000/shop/success' + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://localhost:3000/shop/cancel',
        metadata={
            'user_id': user.id,
            'tickets': 15
        }
    )


@pytest.mark.django_db
@patch('stripe.checkout.Session.retrieve')
def test_buy_tickets(mock_session_retrieve):
    client = APIClient()
    url = reverse('buy_tickets')  # Assurez-vous que 'buy_tickets' est bien le nom de votre vue dans les urls

    # Créer un utilisateur pour le test
    user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
    token = Token.objects.create(user=user)

    # Ajouter le token à l'en-tête de la requête
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # Mock de la réponse de Stripe pour simuler la récupération de la session
    mock_session_retrieve.return_value = MagicMock(payment_status='paid', metadata={'tickets': 15})

    # Vérifier que le profil utilisateur a été créé et mis à jour
    assert hasattr(user, 'profile')
    assert user.profile.tickets == 5


@pytest.mark.django_db
def test_get_history():
    client = APIClient()
    url = reverse('get_history')  # Assurez-vous que 'get_history' est bien le nom de votre vue dans les urls

    # Créer un utilisateur pour le test
    user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
    token = Token.objects.create(user=user)

    # Ajouter le token à l'en-tête de la requête
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # Créer des entrées d'historique pour l'utilisateur
    History.objects.create(user=user, ville='TestVille1', magasin='TestMagasin1', nb_ticket_en_cours=5, type_scrap='test')
    History.objects.create(user=user, ville='TestVille2', magasin='TestMagasin2', nb_ticket_en_cours=10, type_scrap='test')

    # Exécuter la requête GET
    response = client.get(url)

    # Vérifier la réponse
    assert response.status_code == status.HTTP_200_OK

    # Vérifier que les données retournées sont correctes en utilisant le serializer
    expected_data = History.objects.filter(user=user).order_by('-id')
    serializer = HistorySerializer(expected_data, many=True)
    assert response.data == serializer.data

@pytest.mark.django_db
def test_submit_form_basique():
    
    user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # Données de test pour la requête POST
    data = {'brand': 'TestBrand', 'city': 'TestCity'}

    # Exécuter la requête POST
    response = client.post(reverse('submit_form_basique'), data)

    # Vérifier que l'objet History a été créé avec les bonnes valeurs
    history_entry = History.objects.get(user=user)
    assert history_entry.ville == 'TestCity'
    assert history_entry.magasin == 'TestBrand'
    assert history_entry.type_scrap == 'basique'


@pytest.fixture
def setup_test():
    # Créer un utilisateur de test avec un profile s'il n'existe pas encore
    user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
    if not hasattr(user, 'profile'):
        profile = Profile.objects.create(user=user, tickets=10)  # Créer un profile avec des tickets
    else:
        profile = user.profile
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client, user

@pytest.mark.django_db
def test_get_user_info(setup_test):
    client, user = setup_test

    # Exécuter la requête GET
    response = client.get(reverse('get_user_info'))

    # Vérifier la réponse
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == user.username
    assert response.data['tickets'] == user.profile.tickets


