#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
import re
import urllib2
import urllib
import json
import base64
from telebot import types

userStep = {}
knownUsers = []

with open("./spoti.TOKEN", "r") as TOKEN:
    bot = telebot.TeleBot(TOKEN.read().strip())
with open("./spotiID.token", "r") as ID:
    clientID = ID.read().strip()
with open("./spotiSec.token", "r") as sec:
    clientSecret = sec.read().strip()
    
# Detects new users
def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print ("Nuevo usuario detectado")
        return 0

def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print (str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)

# Create bot
bot.set_update_listener(listener)

def encodeUserData():
    return (base64.urlsafe_b64encode(clientID + ":" + clientSecret))


def solicita_token():
    url = 'https://accounts.spotify.com/api/token'
    authorization = encodeUserData()
    data  = {
        'grant_type' : 'client_credentials'
        } 

    data_encoded = urllib.urlencode(data)
    req = urllib2.Request(url, data_encoded)
    req.add_header( 'Authorization' , 'Basic ' + authorization)
    res = urllib2.urlopen(req)
    token = json.loads(res.read())['access_token']
    return token

def enviaPet(tipo,uri):
    token = solicita_token()
    info = {}
    url = url = "https://api.spotify.com/v1/" + tipo + "s/" + uri
    req = urllib2.Request(url)
    req.add_header( 'Authorization' , 'Bearer ' + token)
    res = urllib2.urlopen(req)
    jso = json.loads(res.read())
    if tipo == "track":
        tit = jso['name']
        alb = jso['album']['name']
        art = jso['artists'].pop()['name']
        url = jso['external_urls']['spotify']
        info = {'tit': tit,
                'alb': alb,
                'art': art,
                'url': url}
    else:
        nom = jso['name']
        art = jso['artists'].pop()['name']
        url = jso['external_urls']['spotify']
        info = (nom,art)
        info = {'nom': nom,
                'art': art,
                'url': url}
    return info

# Handlers
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hola! Pásame una URI de canción de Spotify y te devolveré su información")

@bot.message_handler(content_types=['text'])
def handle_uri(message):
    match = re.search('spotify:(track|album):([a-zA-Z0-9]+)',message.text)
    tipo = ""
    uri = ""
    markup = types.InlineKeyboardMarkup()
    
    if match is not None:
        tipo = match.group(1)
        uri = match.group(2)
        info = enviaPet(tipo,uri)
        if tipo == "track":
            tit = info['tit']
            alb = info['alb']
            art = info['art']
            url = info['url']
            bt = types.InlineKeyboardButton("Abrir en Spotify Web",url=url)
            markup.add(bt)
            bot.reply_to(message, u"Título de la canción: " + tit + "\nArtista: "+art+u"\nÁlbum: "+alb, reply_markup=markup)
        else:
            nom = info['nom']
            art = info['art']
            url = info['url']
            bt = types.InlineKeyboardButton("Abrir en Spotify Web",url=url)
            markup.add(bt)
            bot.reply_to(message, u"Nombre del álbum: " + nom + "\nArtista: "+art)
        
# Ignora mensajes antiguos
bot.skip_pending = True

# Ejecuta...
print("Running...")
bot.polling()
