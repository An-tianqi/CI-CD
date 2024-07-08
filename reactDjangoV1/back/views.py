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

import stripe

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
import os

options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if username is None or password is None or email is None:
        return Response({'error': 'Please provide username, password and email'}, status=400)
    try:
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        # Vérifiez si le profil existe déjà avant de le créer
        profile, created = Profile.objects.get_or_create(user=user)

        return Response({'message': 'User created successfully'}, status=201)
    except IntegrityError:
        return Response({'error': 'This username already exists'}, status=400)

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response("Invalid credentials", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def logout_view(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logout successful'}, status=200)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def create_checkout_session(request):
    user = request.user
    try:
        tickets_to_add = int(request.data.get('tickets', 0))
    except ValueError:
        return Response({'message': 'Invalid number of tickets'}, status=status.HTTP_400_BAD_REQUEST)

    if tickets_to_add <= 0:
        return Response({'message': 'Invalid number of tickets'}, status=status.HTTP_400_BAD_REQUEST)

    # Définir le prix en fonction du nombre de tickets
    if tickets_to_add == 5:
        unit_amount = 499  # 4.99 USD EUR ticket
    elif tickets_to_add == 15:
        unit_amount = 1499  # 14.99 EUR par ticket
    elif tickets_to_add == 30:
        unit_amount = 2999  # 29.99 EUR par ticket
    else:
        return Response({'message': 'Invalid number of tickets'}, status=status.HTTP_400_BAD_REQUEST)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': f'{tickets_to_add} Tickets',
                },
                'unit_amount': unit_amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:3000/shop/success' + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://localhost:3000/shop/cancel',
        metadata={
            'user_id': user.id,
            'tickets': tickets_to_add
        }
    )

    return Response({'sessionId': session.id})



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def buy_tickets(request):
    user = request.user
    session_id = request.data.get('session_id', None)

    if session_id is None:
        return Response({'message': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            tickets_to_add = int(session.metadata.tickets)
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)
            user.profile.tickets += tickets_to_add
            user.profile.save()
            return Response({'message': 'Tickets purchased successfully', 'tickets': user.profile.tickets})
        else:
            return Response({'message': 'Payment not successful'}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.StripeError as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def get_history(request):
    user = request.user
    history_entries = History.objects.filter(user=user).order_by('-id')
    serializer = HistorySerializer(history_entries, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def submit_form_medium(request):
    user = request.user

    # Ensure the user has a profile
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)

    if user.profile.tickets >= 1:
        user.profile.tickets -= 1
        user.profile.save()
        print("medium")
        enseigne = request.data.get('brand')
        ville = request.data.get('city')

        # Enregistrer l'historique
        History.objects.create(user=user, ville=ville, magasin=enseigne, nb_ticket_en_cours=user.profile.tickets, type_scrap='medium')

        # Suite du code de scraping...
        url2 = "https://www.google.com/search?q=" + enseigne + "+" + ville + "&rlz=1C5GCEM_en&biw=1848&bih=968&tbm=lcl&ei=apkhZLSKGsbVkdUP1oabuAY&ved=0ahUKEwi058D5mvz9AhXGaqQEHVbDBmcQ4dUDCAg&uact=5&oq=" + enseigne + "+" + ville + "&gs_lcp=Cg1nd3Mtd2l6LWxvY2FsEAMyCAgAEIAEELEDMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEOgcIABCKBRBDOgYIABAWEB46CwgAEIAEELEDEIMBOgoIABCKBRCxAxBDUP8KWOjchgFgjN6GAWgHcAB4AIABfIgB-AySAQQxOC4ymAEAoAEBsAEAwAEB&sclient=gws-wiz-local#rlfi=hd:;si:;mv:[[72.59981891874918,78.7458826694124],[24.315754054065685,-46.76192983058759]];start:{page}"
        pages = range(0, 40, 20)
        MAG = []
        PHONE = []
        TYPE = []
        ADR = []
        ZIP = []
        CITY = []
        WEB = []
        HORAIRE = []
        IMAGE = []

        options = FirefoxOptions()
        options.add_argument("--headless")
        service = FirefoxService()

        with webdriver.Firefox(service=service, options=options) as driver:
            try:
                driver.get(url2)
                time.sleep(1)
                back = driver.find_elements(By.CSS_SELECTOR, "div[class='lssxud']")[1]
                back.click()

                for page in pages:
                    print("page")
                    print(page)
                    driver.get(url2.format(page=page, ville=ville))
                    time.sleep(2)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    time.sleep(1)

                    stores_verif = soup.find_all("div", class_="rllt__details")
                    stores = driver.find_elements(By.CSS_SELECTOR, "div[class='rllt__details']")
                    if stores_verif == []:
                        break
                    print("------")

                    for x in range(23):
                        stores2 = driver.find_elements(By.CSS_SELECTOR, "div[class='rllt__details']")
                        time.sleep(0.5)
                        try:
                            stores2[x].click()
                            soup2 = BeautifulSoup(driver.page_source, 'html.parser')
                            time.sleep(0.5)
                            try:
                                adr_complete = soup2.find("div", {"data-attrid": "kc:/location/location:address"}).text
                            except:
                                adr_complete = ""
                            try:
                                name = soup2.find("h2", {"data-dtype": "d3ifr"}).text
                            except:
                                name = ""
                            try:
                                type = soup2.find("span", class_="YhemCb").text
                            except:
                                type = ""
                            try:
                                horaire = soup2.find("table", class_="WgFkxc").text
                            except:
                                horaire = ""
                            try:
                                jours_semaine = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
                            except:
                                jours_semaine = ""

                            try:
                                pattern = rf'({"|".join(jours_semaine)})((?:\d{{2}}:\d{{2}}–\d{{2}}:\d{{2}}|Fermé))+'
                                matches = re.findall(pattern, horaire)
                                horaires = {jour: heures if "Fermé" not in heures else "Fermé" for jour, heures in matches}
                                horaires_json = json.dumps(horaires, ensure_ascii=False)
                            except:
                                horaires_json = ""
                            try:
                                zip_code = adr_complete.split(",")[1].split(" ")[1]
                            except:
                                zip_code = ""
                            try:
                                city = adr_complete.split(",")[1].split(" ")[2]
                            except:
                                city = ""
                            image_url = ""
                            try:
                                style = soup2.find("button", {"data-clid": "local-photo-browser"}).find("div").get("style")
                                parts = style.split("url(")
                                image_url = parts[1].strip(")\"'")
                            except:
                                img = "no"
                            try:
                                phone = soup2.find("span", class_="LrzXr zdqRlf kno-fv").text
                            except:
                                phone = ""
                            try:
                                web = soup2.find("a", class_="xFAlBc").text
                            except:
                                web = ""
                            print(f"{name};{zip_code};{city};{adr_complete};{phone};{web};{horaires_json};{type};{image_url} ")
                            MAG.append(name)
                            ZIP.append(zip_code)
                            CITY.append(city)
                            ADR.append(adr_complete)
                            PHONE.append(phone)
                            WEB.append(web)
                            HORAIRE.append(horaires_json)
                            TYPE.append(type)
                            IMAGE.append(image_url)
                        except:
                            print("erreur mag")
                            continue
            except Exception as e:
                print(f"Erreur WebDriver : {e}")

# response = HttpResponse()
# response['Content-Disposition'] = 'attachment; filename=' + enseigne + '.csv'
# writer = csv.writer(response)
# writer.writerow(['Nom Magasin', 'Type', 'Adresse', 'Numero Tel'])
# for (name, type, zip_code, city, adr_complete, phone, horaires_json, web, image_url) in zip(MAG, TYPE, ZIP, CITY, ADR, PHONE, HORAIRE, WEB, IMAGE):
# writer.writerow([name, type, zip_code, city, adr_complete, phone, horaires_json, web, image_url])

# return response

        # Générer le fichier CSV
        file_name = f'{enseigne}_{ville}.csv'
        file_path = os.path.join('temp', file_name)
        if not os.path.exists('temp'):
            os.makedirs('temp')
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Nom Magasin', 'Type', 'Adresse', 'Numero Tel', 'Horaire', 'Web', 'Image'])
            for (name, type, adr_complete, phone, horaires_json, web, image_url) in zip(MAG, TYPE, ADR, PHONE, HORAIRE, WEB, IMAGE):
                writer.writerow([name, type, adr_complete, phone, horaires_json, web, image_url])

        # Envoyer le fichier par email
        try:
            with get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS
            ) as connection:
                subject = 'Résultats de votre scraping'
                message = f'Bonjour {user.username},\n\nVoici les résultats de votre scraping premium pour {enseigne} à {ville}.'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email]

                email = EmailMessage(subject, message, email_from, recipient_list, connection=connection)
                email.attach_file(file_path)
                email.send()

            # Supprimer le fichier temporaire après l'envoi de l'email
            os.remove(file_path)
            return Response({"message": "Scraping réussi et résultats envoyés par email!"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return Response({"message": "Scraping réussi, mais l'envoi de l'email a échoué."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"message": "Vous n'avez plus de tickets. Voulez-vous être redirigé vers la page de boutique ?"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def submit_form_prenium(request):
    user = request.user

    # Ensure the user has a profile
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)

    if user.profile.tickets >= 3:
        user.profile.tickets -= 3
        user.profile.save()
        print("prenium")
        enseigne = request.data.get('brand')
        ville = request.data.get('city')

        # Enregistrer l'historique
        History.objects.create(user=user, ville=ville, magasin=enseigne, nb_ticket_en_cours=user.profile.tickets, type_scrap='premium')

        url2 = "https://www.google.com/search?q=" + enseigne + "+" + ville + "&rlz=1C5GCEM_en&biw=1848&bih=968&tbm=lcl&ei=apkhZLSKGsbVkdUP1oabuAY&ved=0ahUKEwi058D5mvz9AhXGaqQEHVbDBmcQ4dUDCAg&uact=5&oq=" + enseigne + "+" + ville + "&gs_lcp=Cg1nd3Mtd2l6LWxvY2FsEAMyCAgAEIAEELEDMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEOgcIABCKBRBDOgYIABAWEB46CwgAEIAEELEDEIMBOgoIABCKBRCxAxBDUP8KWOjchgFgjN6GAWgHcAB4AIABfIgB-AySAQQxOC4ymAEAoAEBsAEAwAEB&sclient=gws-wiz-local#rlfi=hd:;si:;mv:[[72.59981891874918,78.7458826694124],[24.315754054065685,-46.76192983058759]];start:{page}"
        pages = range(0, 40, 20)
        MAG = []
        PHONE = []
        TYPE = []
        ADR = []
        ZIP = []
        CITY = []
        WEB = []
        HORAIRE = []
        IMAGE = []
        EMAILS = []

        options = FirefoxOptions()
        options.add_argument("--headless")
        service = FirefoxService()

        with webdriver.Firefox(service=service, options=options) as driver:
            try:
                driver.get(url2)
                time.sleep(1)
                back = driver.find_elements(By.CSS_SELECTOR, "div[class='lssxud']")[1]
                back.click()

                for page in pages:
                    print("page")
                    print(page)
                    driver.get(url2.format(page=page, ville=ville))
                    time.sleep(2)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    time.sleep(1)

                    stores_verif = soup.find_all("div", class_="rllt__details")
                    stores = driver.find_elements(By.CSS_SELECTOR, "div[class='rllt__details']")
                    if stores_verif == []:
                        break
                    print("------")

                    for x in range(23):
                        stores2 = driver.find_elements(By.CSS_SELECTOR, "div[class='rllt__details']")
                        time.sleep(0.5)
                        try:
                            stores2[x].click()
                            soup2 = BeautifulSoup(driver.page_source, 'html.parser')
                            time.sleep(0.5)
                            try:
                                adr_complete = soup2.find("div", {"data-attrid": "kc:/location/location:address"}).text
                            except:
                                adr_complete = ""
                            try:
                                name = soup2.find("h2", {"data-dtype": "d3ifr"}).text
                            except:
                                name = ""
                            try:
                                type = soup2.find("span", class_="YhemCb").text
                            except:
                                type = ""
                            try:
                                horaire = soup2.find("table", class_="WgFkxc").text
                            except:
                                horaire = ""
                            try:
                                jours_semaine = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
                            except:
                                jours_semaine = ""

                            try:
                                pattern = rf'({"|".join(jours_semaine)})((?:\d{{2}}:\d{{2}}–\d{{2}}:\d{{2}}|Fermé))+'
                                matches = re.findall(pattern, horaire)
                                horaires = {jour: heures if "Fermé" not in heures else "Fermé" for jour, heures in matches}
                                horaires_json = json.dumps(horaires, ensure_ascii=False)
                            except:
                                horaires_json = ""
                            try:
                                zip_code = adr_complete.split(",")[1].split(" ")[1]
                            except:
                                zip_code = ""
                            try:
                                city = adr_complete.split(",")[1].split(" ")[2]
                            except:
                                city = ""
                            image_url = ""
                            try:
                                style = soup2.find("button", {"data-clid": "local-photo-browser"}).find("div").get("style")
                                parts = style.split("url(")
                                image_url = parts[1].strip(")\"'")
                            except:
                                img = "no"
                            try:
                                phone = soup2.find("span", class_="LrzXr zdqRlf kno-fv").text
                            except:
                                phone = ""
                            try:
                                web = soup2.find("a", class_="xFAlBc").text
                            except:
                                web = ""
                            print(f"{name};{zip_code};{city};{adr_complete};{phone};{web};{horaires_json};{type};{image_url} ")
                            MAG.append(name)
                            ZIP.append(zip_code)
                            CITY.append(city)
                            ADR.append(adr_complete)
                            PHONE.append(phone)
                            WEB.append(web)
                            HORAIRE.append(horaires_json)
                            TYPE.append(type)
                            IMAGE.append(image_url)
                        except:
                            print("erreur mag")
                            continue
            except Exception as e:
                print(f"Erreur WebDriver : {e}")

        print(EMAILS)
        # response = HttpResponse()
        # response['Content-Disposition'] = 'attachment; filename=' + enseigne + '.csv'
        # writer = csv.writer(response)
        # writer.writerow(['Nom Magasin', 'Type', 'Adresse', 'Numero Tel', 'Horaires', 'Web', 'Image', 'Emails'])
        # for (name, type, zip_code, city, adr_complete, phone, horaires_json, web, image_url, emails) in zip(MAG, TYPE, ZIP, CITY, ADR, PHONE, HORAIRE, WEB, IMAGE, EMAILS):
        #     writer.writerow([name, type, zip_code, city, adr_complete, phone, horaires_json, web, image_url, emails])

        # return response
            # Générer le fichier CSV
        file_name = f'{enseigne}_{ville}_premium.csv'
        file_path = os.path.join('temp', file_name)
        if not os.path.exists('temp'):
            os.makedirs('temp')
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Nom Magasin', 'Type', 'Adresse', 'Numero Tel', 'Horaires', 'Web', 'Image', 'Emails'])
            for (name, type, adr_complete, phone, horaires_json, web, image_url) in zip(MAG, TYPE, ADR, PHONE, HORAIRE, WEB, IMAGE):
                writer.writerow([name, type, adr_complete, phone, horaires_json, web, image_url])

        # Envoyer le fichier par email
        try:
            with get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS
            ) as connection:
                subject = 'Résultats de votre scraping premium'
                message = f'Bonjour {user.username},\n\nVoici les résultats de votre scraping premium pour {enseigne} à {ville}.'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email]

                email = EmailMessage(subject, message, email_from, recipient_list, connection=connection)
                email.attach_file(file_path)
                email.send()

            # Supprimer le fichier temporaire après l'envoi de l'email
            os.remove(file_path)
            return Response({"message": "Scraping premium réussi et résultats envoyés par email!"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return Response({"message": "Scraping premium réussi, mais l'envoi de l'email a échoué."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"message": "Vous n'avez plus de tickets. Voulez-vous être redirigé vers la page de boutique ?"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def submit_form_basique(request):
    user = request.user
    logging.info(f"User {user.username} started a basic scrape.")
    print("basique")

    enseigne = request.data.get('brand')
    ville = request.data.get('city')

    History.objects.create(user=user, ville=ville, magasin=enseigne, nb_ticket_en_cours=user.profile.tickets, type_scrap='basique')

    url2 = "https://www.google.com/search?q=" + enseigne + "+" + ville + "&rlz=1C5GCEM_en&biw=1848&bih=968&tbm=lcl&ei=apkhZLSKGsbVkdUP1oabuAY&ved=0ahUKEwi058D5mvz9AhXGaqQEHVbDBmcQ4dUDCAg&uact=5&oq=" + enseigne + "+" + ville + "&gs_lcp=Cg1nd3Mtd2l6LWxvY2FsEAMyCAgAEIAEELEDMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEOgcIABCKBRBDOgYIABAWEB46CwgAEIAEELEDEIMBOgoIABCKBRCxAxBDUP8KWOjchgFgjN6GAWgHcAB4AIABfIgB-AySAQQxOC4ymAEAoAEBsAEAwAEB&sclient=gws-wiz-local#rlfi=hd:;si:;mv:[[72.59981891874918,78.7458826694124],[24.315754054065685,-46.76192983058759]];start:{page}"
    pages = range(0, 40, 20)
    MAG = []
    PHONE = []
    TYPE = []
    ADR = []

    options = FirefoxOptions()
    options.add_argument("--headless")
    service = FirefoxService()

    with webdriver.Firefox(service=service, options=options) as driver:
        try:
            driver.get(url2)
            time.sleep(1)
            back = driver.find_elements(By.CSS_SELECTOR, "div[class='lssxud']")[1]
            back.click()
            for page in pages:
                print("lets go")
                driver.get(url2.format(page=page))
                time.sleep(3)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                time.sleep(2)
                stores = soup.find_all("div", class_="rllt__details")
                print("----")
                for store in stores:
                    print(store)
                    try:
                        mag = store.find_all("div")[0].text
                    except:
                        mag = ""
                    try:
                        type = store.find_all("div")[1].text
                    except:
                        type = ""
                    try:
                        adr = store.find_all("div")[2].text.split(" · ")[0]
                    except:
                        adr = ""
                    try:
                        tel = store.find_all("div")[2].text.split(" · ")[1]
                    except:
                        tel = ""
                    print("-------Mag------")
                    print(mag)
                    print(type)
                    print(adr)
                    print(tel)
                    MAG.append(mag)
                    TYPE.append(type)
                    ADR.append(adr)
                    PHONE.append(tel)

            # response = HttpResponse()
            # response['Content-Disposition'] = 'attachment; filename=' + enseigne + '.csv'
            # writer = csv.writer(response)
            # writer.writerow(['Nom Magasin', 'Type', 'Adresse', 'Numero Tel'])
            # for (name, type, adr, phone) in zip(MAG, TYPE, ADR, PHONE):
            #     writer.writerow([name, type, adr, phone])

            # return response

            # Générer le fichier CSV
            file_name = f'{enseigne}_{ville}_basique.csv'
            file_path = os.path.join('temp', file_name)
            if not os.path.exists('temp'):
                os.makedirs('temp')
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Nom Magasin', 'Type', 'Adresse', 'Numero Tel'])
                for (name, type, adr, phone) in zip(MAG, TYPE, ADR, PHONE):
                    writer.writerow([name, type, adr, phone])

            # Envoyer le fichier par email
            try:
                with get_connection(
                    host=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    username=settings.EMAIL_HOST_USER,
                    password=settings.EMAIL_HOST_PASSWORD,
                    use_tls=settings.EMAIL_USE_TLS
                ) as connection:
                    subject = 'Résultats de votre scraping basique'
                    message = f'Bonjour {user.username},\n\nVoici les résultats de votre scraping basique pour {enseigne} à {ville}.'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [user.email]

                    email = EmailMessage(subject, message, email_from, recipient_list, connection=connection)
                    email.attach_file(file_path)
                    email.send()

                # Supprimer le fichier temporaire après l'envoi de l'email
                os.remove(file_path)
                return Response({"message": "Scraping basique réussi et résultats envoyés par email!"}, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email: {e}")
                return Response({"message": "Scraping basique réussi, mais l'envoi de l'email a échoué."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print(f"Erreur WebDriver : {e}")
            return JsonResponse({"message": "Code mal exécuté"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    response_data = {
        'username': user.username,
        'tickets': user.profile.tickets,  # Assurez-vous que ce champ existe dans votre modèle User
    }
    return Response(response_data)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny])
def contact(request):
    user = request.user
    name = request.data.get('name')
    subject = request.data.get('subject')
    message = request.data.get('message')

    if not name or not subject or not message:
        return Response({"message": "Tous les champs sont requis."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS
        ) as connection:
            email_subject = f"Scrap4you: {subject}"
            email_body = f"Message de {name}, ({user.email}):\n\n{message}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [settings.EMAIL_HOST_USER]

            email = EmailMessage(email_subject, email_body, email_from, recipient_list, headers={'Reply-To': user.email}, connection=connection)
            email.send()

        return Response({"message": "Votre message a été envoyé avec succès!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": f"Une erreur s'est produite lors de l'envoi de l'email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)