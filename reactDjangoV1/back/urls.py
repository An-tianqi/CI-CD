from django.contrib import admin
from django.urls import path, include
from .views import signup,login,submit_form_medium, submit_form_basique, submit_form_prenium, buy_tickets, get_history,logout_view,get_user_info, create_checkout_session, contact
urlpatterns = [
    #path('register', RegisterView.as_view(), name='register'),
    #path('buy_tickets', buy_tickets, name='buy_tickets'),
    path('signup', signup),
    path('login', login),
    path('submit_form_basique', submit_form_basique, name='submit_form_basique'),
    path('submit_form_medium', submit_form_medium, name='submit_form_medium'),
    path('submit_form_prenium', submit_form_prenium, name='submit_form_prenium'),
    path('buy_tickets', buy_tickets, name='buy_tickets'),
    path('history/', get_history, name='get_history'),
    path('logout/', logout_view, name='logout'),
    path('user/', get_user_info, name='get_user_info'),  # Nouvelle route pour obtenir les informations de l'utilisateur
    path('create_checkout_session', create_checkout_session, name='create_checkout_session'),
    path('contact/', contact, name='contact'),
]


