#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *

import sqlite3
import hashlib
from datetime import datetime

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

# odkomentiraj, če želiš sporočila o napakah
debug(True)

#Mapa s statičnimi datotekami
static_dir = "./static"

#piškotki
secret = "to skrivnost je zelo tezko uganiti 1094107c907cw982982c42"


######################################################################
#Pomožne funkcije

def password_hash(s):
    """Vrni SHA-512 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.sha512()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

# Funkcija, ki v cookie spravi sporocilo

def set_sporocilo(tip, vsebina):
    response.set_cookie('message', (tip, vsebina), path='/', secret=secret)

# Funkcija, ki iz cookija dobi sporočilo, če je
# kot brskalnik vrnemo cookie, pod nekim ključem lahko zbrisemo ali dodamo in potem vrnemo
def get_sporocilo():
    sporocilo = request.get_cookie('message', default=None, secret=secret)
    response.delete_cookie('message')
    return sporocilo

# To smo dobili na http://stackoverflow.com/questions/1551382/user-friendly-time-format-in-python
# in predelali v slovenščino. Da se še izboljšati, da bo pravilno delovala dvojina itd.
def pretty_date(time):
    """
    Predelaj čas (v formatu Unix epoch) v opis časa, na primer
    'pred 4 minutami', 'včeraj', 'pred 3 tedni' ipd.
    """

    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "zdaj"
        if second_diff < 60:
            return "pred " + str(second_diff) + " sekundami"
        if second_diff < 120:
            return  "pred minutko"
        if second_diff < 3600:
            return "pred " + str( second_diff // 60 ) + " minutami"
        if second_diff < 7200:
            return "pred eno uro"
        if second_diff < 86400:
            return "pred " + str( second_diff // 3600 ) + " urami"
    if day_diff == 1:
        return "včeraj"
    if day_diff < 7:
        return "pred " + str(day_diff) + " dnevi"
    if day_diff < 31:
        return "pred " + str(day_diff//7) + " tedni"
    if day_diff < 365:
        return "pred " + str(day_diff//30) + " meseci"
    return "pred " + str(day_diff//365) + " leti"


#najpomebnejša funkcija
def get_user(auto_login = True):
    """Poglej cookie in ugotovi, kdo je prijavljeni uporabnik,
       vrni njegov username in ime. Če ni prijavljen, presumeri
       na stran za prijavo ali vrni None (advisno od auto_login).
    """
    username = request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        cur.execute("SELECT uporabnisko_ime, ime FROM uporabnik WHERE uporabnisko_ime=%s",
                  [username])
        r = cur.fetchone()
       # cur.close ()
        if r is not None:
            # uporabnik obstaja, vrnemo njegove podatke
            # če smo te našli v bazi te vrnemo
            return r
    # Če pridemo do sem, uporabnik ni prijavljen, naredimo redirect
    # če v cookiju nismo ugotovili kdo smo, te da na login stran
    # zdaj preusmerimo na login, saj ni vrnilo username
    if auto_login:
        redirect('/login/')
    else:
        return None
    # get user torej naredi dve stvari
    # ali smo user ki je že v bazi
    # ali pa te preusmeri na lgoin stran

######################################################################
# Funkcije, ki obdelajo zahteve odjemalcev.

@route("/zivjo/")
def krena():
    return "Živjo"

# ??
@route("/static/<filename:path>")
def static(filename):
    """Splošna funkcija, ki servira vse statične datoteke iz naslova
       /static/..."""
    return static_file(filename, root=static_dir)

# ??

@route("/")
def main():
    """Glavna stran."""
    (username, ime) = get_user() 
    # Morebitno sporočilo za uporabnika
    sporocilo = get_sporocilo()
    # Vrnemo predlogo za glavno stran
    # izriši spletno stran iz predloge, to je pol html pa pol luknje
    # na praznih mestih povemo kaj moramo not vstavit
    # main html je pod views
    # torej uporabi predlogo main.html, da jo napolni rabis 4 spremenljivke in vrni kot html
    #return template("main.html",
    #                       ime=ime,
    #                       username=username,
    #                       sporocilo=sporocilo)
    return "glavna stran"
#obstaja večov tipov zahtevkov v protokolu http, get, post, delete, put,...
#get request -> če samo gremo na ta link
#post request, če moramo kam it na strežnik in nek gumb pritisnit

@get("/login/")
def login_get():
    """Serviraj formo za login."""
    return template("login.html",
                          napaka=None,
                         username=None)

@post("/login/")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = request.forms.username
    # Izračunamo hash gesla, ki ga bomo spravili
    geslo = password_hash(request.forms.password)
    #geslo = request.forms.password
    # Preverimo, ali se je uporabnik pravilno prijavil
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
    cur.execute("SELECT * FROM uporabnik WHERE uporabnisko_ime=%s AND geslo=%s",
                [username, geslo])
    if cur.fetchone() is None:
        # Username in geslo se ne ujemata
        return template("login.html",
                               napaka="Nepravilna prijava",
                               username=username)
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        response.set_cookie('uporabnisko_ime', username, path='/', secret=secret)
        redirect("/")

@get("/logout/")
def logout():
    """Pobriši cookie in preusmeri na login."""
    response.delete_cookie('uporabnisko_ime')
    redirect('/login/')

@get("/register/")
def login_get():
    """Prikaži formo za registracijo."""
    return template("register.html", 
                           username=None,
                           ime=None,
                           napaka=None)

@post("/register/")
def register_post():
    """Registriraj novega uporabnika."""
    username = request.forms.username
    ime = request.forms.ime
    password1 = request.forms.password1
    password2 = request.forms.password2
    # Ali uporabnik že obstaja?
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
    cur.execute("SELECT 1 FROM uporabnik WHERE uporabnisko_ime=%s", [username])
    if cur.fetchone():
        # Uporabnik že obstaja
        return template("register.html",
                               username=username,
                               ime=ime,
                               napaka='To uporabniško ime je že zavzeto')
    elif not password1 == password2:
        # Geslo se ne ujemata
        return template("register.html",
                               username=username,
                               ime=ime,
                               napaka='Gesli se ne ujemata')
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        password = password_hash(password1)
        cur.execute("INSERT INTO uporabnik (uporabnisko_ime, ime, geslo) VALUES (%s, %s, %s)",
                  (username, ime, password1))
        # Daj uporabniku cookie
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")



######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080) #,reloader=True)

