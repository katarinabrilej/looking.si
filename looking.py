#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *

import sqlite3
import hashlib
from datetime import datetime
from datetime import date

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

# odkomentiraj, če želiš sporočila o napakah
debug(True)

#Mapa s statičnimi datotekami
static_dir = "./static"
hotel_dir = "./hotel"

#piškotki
secret = "to skrivnost je zelo tezko uganiti 1094107c907cw982982c42"


######################################################################
#Pomožne funkcije

def password_hash(s):
    """Vrni SHA-512 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
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

#najpomebnejša funkcija
def get_user():
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
            return username
    # Če pridemo do sem, uporabnik ni prijavljen, naredimo redirect
    # če v cookiju nismo ugotovili kdo smo, te da na login stran
    # zdaj preusmerimo na login, saj ni vrnilo username
    else:
        return None
    # get user torej naredi dve stvari
    # ali smo user ki je že v bazi
    # ali pa te preusmeri na lgoin stran

######################################################################
# Funkcije, ki obdelajo zahteve odjemalcev.
def clean(list):
    cleaned = []
    for x in list:
        strip = x[0].strip()
        cleaned.append(strip)
    return cleaned

def clean2(list):
    cleaned = []
    for x in list:
        strip1 = x[0].strip()
        strip2 = x[1]
        cleaned.append([strip1,strip2])
    return cleaned

def clean3(list):
    cleaned = []
    for x in list:
        cleaned.append(x[0])
    return cleaned

    
def drzave():
    cur.execute("SELECT ime_mesta, ime_drzave,  mesto.id ,drzava.id FROM drzava JOIN mesto ON drzava.id = drzava_id ORDER BY ime_mesta")
    drzave = cur.fetchall()
    return drzave


@route("/static/<filename:path>")
def static(filename):
    """Splošna funkcija, ki servira vse statične datoteke iz naslova
       /static/..."""
    return static_file(filename, root=static_dir)

@route("/hotel/<filename:path>")
def hotel(filename):
    return static_file(filename, root=hotel_dir)


@get("/")
def main():
    username = get_user() 
    drzave_seznam = drzave()
    sporocilo = get_sporocilo()
    return template("index.html", drzave=drzave_seznam,
                           username=username,
                           sporocilo=sporocilo)

@get("/drzava/:x")
def drzave_hoteli(x):
    username = get_user()
    cur.execute("SELECT hotel_id, lokacija_id FROM na_lokaciji")
    na_lokaciji = cur.fetchall()
    cur.execute("SELECT hotel, ugodnost FROM ima")
    ugodnosti_hoteli = cur.fetchall()
    cur.execute("SELECT ime_mesta FROM mesto WHERE id = %s", [x])
    mesto = cur.fetchall()
    mesto = mesto[0][0]
    cur.execute("SELECT id, ime_ugodnosti FROM ugodnosti ORDER BY ime_ugodnosti")
    ugodnosti = cur.fetchall()
    cur.execute("SELECT  lokacije.id,ime_lokacije, tip, mesto.id FROM lokacije JOIN mesto ON mesto_id = mesto.id WHERE mesto.id = %s", [x])
    lokacije = cur.fetchall()
    cur.execute("SELECT ime, hotel.id, st_zvezdic, tip_nastanitve, mesto.id FROM hotel JOIN mesto ON  mesto.id = mesto_id WHERE mesto.id = %s", [x])
    hoteli = cur.fetchall()
    cur.execute("SELECT st_zvezdic, mesto_id FROM hotel WHERE mesto_id =%s", [x])
    zvezdice = cur.fetchall()
    zvezdice = clean3(zvezdice)
    zvezdice = set(zvezdice)
    zvezdice = list(zvezdice)
    cur.execute("SELECT tip_nastanitve, mesto_id FROM hotel WHERE mesto_id =%s", [x])
    nastanitve = cur.fetchall()
    nastanitve = clean(nastanitve)
    nastanitve = set(nastanitve)
    nastanitve = list(nastanitve)
    return template("drzave.html", username = username, ugodnosti = ugodnosti, lokacije = lokacije, mesto = mesto, hoteli = hoteli, zvezdice = zvezdice, nastanitve = nastanitve, ugodnosti_hoteli = ugodnosti_hoteli, na_lokaciji = na_lokaciji)

@get("/hotel-podrobno/:x")
def hotel1(x):
    cur.execute("SELECT ime_lokacije, tip, lokacija_id FROM na_lokaciji JOIN lokacije ON lokacija_id = id WHERE hotel_id = %s",[x])
    lokacije = cur.fetchall()
    cur.execute("SELECT ugodnost, ime_ugodnosti FROM ima JOIN ugodnosti ON id = ugodnost WHERE hotel = %s", [x])
    ugodnosti = cur.fetchall()
    cur.execute("SELECT hotel.id,ime, st_zvezdic,tip_nastanitve, mesto.ime_mesta FROM hotel JOIN mesto ON mesto.id = mesto_id WHERE hotel.id =%s", [x])
    hotel_podrobnosti = cur.fetchall()
    username = get_user()
    return template("hotel.html", username=username, lokacije = lokacije, ugodnosti = ugodnosti, hotel_podrobnosti = hotel_podrobnosti)

@get("/login/")
def login_get():
    """Serviraj formo za login."""
    return template("login2.html",
                          napaka=None,
                         username=None)

@post("/login/")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = request.forms.username
    # Izračunamo hash gesla, ki ga bomo spravili
    geslo = password_hash(request.forms.password)

   # geslo = request.forms.password
    # Preverimo, ali se je uporabnik pravilno prijavil
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
    cur.execute("SELECT * FROM uporabnik WHERE uporabnisko_ime=%s AND geslo=%s",
                [username, geslo])
    if cur.fetchone() is None:
        # Username in geslo se ne ujemata
        return template("login2.html",
                               napaka="Nepravilna prijava",
                               username=username)
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")



@get("/logout/")
def logout():
    """Pobriši cookie in preusmeri na login."""
    response.delete_cookie('username', path='/')
    redirect('/login/')

@get("/register/")
def login_get():
    """Prikaži formo za registracijo."""
    return template("register2.html", 
                           username=None,
                           ime=None,
                           napaka=None)

@post("/register/")
def register_post():
    """Registriraj novega uporabnika."""
    username = request.forms.username
    ime = request.forms.ime
    priimek = request.forms.priimek
    password1 = request.forms.password1
    password2 = request.forms.password2
    # Ali uporabnik že obstaja?
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
    cur.execute("SELECT 1 FROM uporabnik WHERE uporabnisko_ime=%s", [username])
    if cur.fetchone():
        # Uporabnik že obstaja
        return template("register2.html",
                               username=username,
                               ime=ime,
                               napaka='To uporabniško ime je že zavzeto')
    elif not password1 == password2:
        # Geslo se ne ujemata
        return template("register2.html",
                               username=username,
                               ime=ime,
                               napaka='Gesli se ne ujemata')
    elif username == 'katarinabrilej' or username == 'evadezelak':
        # Vse je v redu, vstavi novega uporabnika v bazo
        uporabnik = "administrator"
        password = password_hash(password1)
        cur.execute("INSERT INTO uporabnik (uporabnisko_ime, ime, priimek, geslo, tip) VALUES (%s, %s, %s, %s, %s)",
                  (username, ime, priimek, password, uporabnik))
         # Daj uporabniku cookie
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        uporabnik = "uporabnik"
        password = password_hash(password1)
        cur.execute("INSERT INTO uporabnik (uporabnisko_ime, ime, priimek, geslo, tip) VALUES (%s, %s, %s, %s, %s)",
                  (username, ime, priimek, password, uporabnik))
        # Daj uporabniku cookie
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")

@get("/uporabnik/")
def uporabnik(sporocila=[]):
    sporocilo = get_sporocilo()
    username = get_user()
    return template("uporabnik.html", username = username, sporocilo = sporocilo,sporocila=sporocila)



@post("/hotel-podrobno/")
def dodajKomentar():
    username = get_user()
    komentar = request.forms.komentar
    ocena = request.forms['optradio']
    datum = date.today()
    #hotel_id = x;
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
    cur.execute("SELECT id FROM uporabnik WHERE uporabnisko_ime=?",[username])
    user_id =  cur.fetchall()
    if user_id is not None:
        cur.execute("INSERT INTO oceni (datum, mnenje, vrednost, hotel, uporabnik) VALUES (%s,%s,%s,%s,%s)",
                                    (datum,komentar,ocena,"6",user_id))
    return template("hotel.html")

@post("/uporabnik/")
def spremeni():
    sporocilo = get_sporocilo()
    username = get_user()
    # Staro geslo (je obvezno)
    password1 = password_hash(request.forms.password1)
    # Preverimo staro geslo
    cur.execute ("SELECT 1 FROM uporabnik WHERE uporabnisko_ime=? AND geslo=?",
               [username, password1])
    # Pokazali bomo eno ali več sporočil, ki jih naberemo v seznam
    sporocila = []
    if cur.fetchone():
        # Geslo je ok
        # Ali je treba spremeniti geslo?
        password2 = request.forms.password2
        password3 = request.forms.password3
        if password2 or password3:
            # Preverimo, ali se gesli ujemata
            if password2 == password3:
                # Vstavimo v bazo novo geslo
                password2 = password_hash(password2)
                cur.execute ("UPDATE uporabnik SET geslo=? WHERE uporabnisko_ime = ?", [password2, username])
                sporocila.append(("alert-success", "Spremenili ste geslo."))
            else:
                sporocila.append(("alert-danger", "Gesli se ne ujemata"))
    else:
        # Geslo ni ok
        sporocila.append(("alert-danger", "Napačno staro geslo"))
    cur.close ()
    # Prikažemo stran z uporabnikom, z danimi sporočili. Kot vidimo,
    # lahko kar pokličemo funkcijo, ki servira tako stran
    return uporabnik(username, sporocila=sporocila)

@get("/admin/")
def admin():
    sporocilo = get_sporocilo()
    username = get_user()
    return template("admin.html", username = username, sporocilo = sporocilo)




######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080) #,reloader=True)
