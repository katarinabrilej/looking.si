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

admini = ["katarinabrilej", "evadezelak", "asistent", "profesor"]
@get("/")
def main():
    username = get_user() 
    drzave_seznam = drzave()
    sporocilo = get_sporocilo()
    return template("index.html", drzave=drzave_seznam,
                           username=username,
                           sporocilo=sporocilo, admini = admini)

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

    cur.execute("SELECT ROUND(AVG(x.vrednost),1),  y.id FROM oceni AS x RIGHT JOIN hotel AS y ON x.hotel = y.id  GROUP BY y.id")
    ocene = cur.fetchall()

    return template("drzave.html", username = username, admini = admini, ugodnosti = ugodnosti, lokacije = lokacije, mesto = mesto, hoteli = hoteli, 
    zvezdice = zvezdice, nastanitve = nastanitve, ugodnosti_hoteli = ugodnosti_hoteli, na_lokaciji = na_lokaciji, ocene = ocene)

@get("/hotel-podrobno/:x")
def hotel1(x):
    cur.execute("SELECT ime_lokacije, tip, lokacija_id FROM na_lokaciji JOIN lokacije ON lokacija_id = id WHERE hotel_id = %s",[x])
    lokacije = cur.fetchall()
    cur.execute("SELECT ugodnost, ime_ugodnosti FROM ima JOIN ugodnosti ON id = ugodnost WHERE hotel = %s", [x])
    ugodnosti = cur.fetchall()
    cur.execute("SELECT hotel.id,ime, st_zvezdic,tip_nastanitve, mesto.ime_mesta FROM hotel JOIN mesto ON mesto.id = mesto_id WHERE hotel.id =%s", [x])
    hotel_podrobnosti = cur.fetchall()
    cur.execute("SELECT datum, mnenje, vrednost,uporabnik.uporabnisko_ime FROM oceni JOIN uporabnik ON uporabnik.id = oceni.uporabnik WHERE hotel= %s", [x])
    komentarji = cur.fetchall()
    username = get_user()
    cur.execute("SELECT AVG(vrednost) FROM oceni WHERE hotel=%s",[x])
    povprecna_ocena = cur.fetchall()
    povprecna_ocena = povprecna_ocena[0][0]
    if povprecna_ocena is not None:
        povprecna_ocena = round(povprecna_ocena,1)
    else:
        povprecna_ocena = 0

    
    return template("hotel.html", username=username, admini = admini, lokacije = lokacije, ugodnosti = ugodnosti, hotel_podrobnosti = hotel_podrobnosti, komentarji = komentarji, povprecna_ocena = povprecna_ocena)

@post("/hotel-podrobno/")
def dodajKomentar():
    username = get_user()
    komentar = request.forms.komentar
    ocena = request.forms['optradio']
    datum = date.today()
    hotel_id = request.forms['idHotela']
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
    cur.execute("SELECT id FROM uporabnik WHERE uporabnisko_ime=%s",[username])
    user_id =  cur.fetchall()
    cur.execute("SELECT ime_lokacije, tip, lokacija_id FROM na_lokaciji JOIN lokacije ON lokacija_id = id WHERE hotel_id = %s",[hotel_id])
    if user_id is not None:
        cur.execute("INSERT INTO oceni (datum, mnenje, vrednost, hotel, uporabnik) VALUES (%s,%s,%s,%s,%s)",
                                    (datum,komentar,ocena,hotel_id,user_id[0][0]))
        return redirect("/hotel-podrobno/"+hotel_id)
       
    


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
    cur.execute("SELECT id FROM uporabnik WHERE uporabnisko_ime=%s",[username])
    user_id =  cur.fetchall()
    cur.execute("SELECT datum, mnenje, vrednost, ime, oceni.hotel FROM oceni JOIN hotel ON oceni.hotel=hotel.id WHERE oceni.uporabnik=%s",[user_id[0][0]])
    mnenja = cur.fetchall()
    
    return template("uporabnik.html", username = username, admini = admini, sporocilo = sporocilo,sporocila=sporocila,mnenja=mnenja)


@post("/uporabnik/")
def spremeni():
    username = get_user()
    # Staro geslo (je obvezno)
    password1 = password_hash(request.forms.password1)
    # Preverimo staro geslo
    cur.execute ("SELECT 1 FROM uporabnik WHERE uporabnisko_ime=%s AND geslo=%s",
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
                cur.execute ("UPDATE uporabnik SET geslo=%s WHERE uporabnisko_ime = %s", [password2, username])
                sporocila.append(("alert-success", "Geslo ste uspešno spremenili."))
            else:
                sporocila.append(("alert-danger", "Gesli se ne ujemata"))
    else:
        # Geslo ni ok
        sporocila.append(("alert-danger", "Staro geslo je napačno"))

    
    # Prikažemo stran z uporabnikom, z danimi sporočili. Kot vidimo,
    # lahko kar pokličemo funkcijo, ki servira tako stran
    return uporabnik(sporocila)

@get("/admin/")
def admin():
    sporocilo = get_sporocilo()
    username = get_user()
    cur.execute("SELECT id, ime_celine FROM celina ORDER BY ime_celine")
    celine= cur.fetchall()
    cur.execute("SELECT id, ime_drzave FROM drzava ORDER BY ime_drzave")
    drzave= cur.fetchall()
    cur.execute("SELECT ime_mesta, ime_drzave,  mesto.id ,drzava.id FROM drzava JOIN mesto ON drzava.id = drzava_id ORDER BY ime_mesta")
    mesta = cur.fetchall()
    cur.execute("SELECT * FROM ugodnosti ORDER BY ime_ugodnosti")
    ugodnosti = cur.fetchall()

    cur.execute("SELECT lokacije.id, mesto_id, ime_lokacije FROM lokacije JOIN mesto on mesto_id = mesto.id WHERE tip = 'Okrožje' ORDER BY ime_lokacije ")
    okrozja_po_mestih = cur.fetchall()
    cur.execute("SELECT lokacije.id, mesto_id, ime_lokacije FROM lokacije JOIN mesto on mesto_id = mesto.id WHERE tip = 'Znamenitost' ORDER BY ime_lokacije ")
    znamenitosti_po_mestih = cur.fetchall()

    return template("admin.html", username = username, sporocilo = sporocilo, napaka1 = None,  napaka2 = None, napaka3 = None, napaka_o = None, napaka_z = None,
    celine = celine, drzave = drzave, mesta = mesta, ugodnosti  = ugodnosti, admini = admini,
    okrozja_po_mestih = okrozja_po_mestih, znamenitosti_po_mestih   = znamenitosti_po_mestih )

@post("/admin/")
def dodaj():
    username = get_user()
    
    cur.execute("SELECT id, ime_celine FROM celina ORDER BY ime_celine")
    celine= cur.fetchall()
    cur.execute("SELECT id, ime_drzave FROM drzava ORDER BY ime_drzave")
    drzave= cur.fetchall()
    cur.execute("SELECT ime_mesta, ime_drzave,  mesto.id ,drzava.id FROM drzava JOIN mesto ON drzava.id = drzava_id ORDER BY ime_mesta")
    mesta = cur.fetchall()
    cur.execute("SELECT * FROM ugodnosti ORDER BY ime_ugodnosti")
    ugodnosti = cur.fetchall()


    cur.execute("SELECT lokacije.id, mesto_id, ime_lokacije FROM lokacije JOIN mesto on mesto_id = mesto.id WHERE tip = 'Okrožje' ORDER BY ime_lokacije ")
    okrozja_po_mestih = cur.fetchall()
    cur.execute("SELECT lokacije.id, mesto_id, ime_lokacije FROM lokacije JOIN mesto on mesto_id = mesto.id WHERE tip = 'Znamenitost' ORDER BY ime_lokacije ")
    znamenitosti_po_mestih = cur.fetchall()


    drzava = request.forms.drzava
    id_celine = request.forms.celina

    mesto = request.forms.mesto
    id_drzave = request.forms.drzava_izbira

    hotel = request.forms.hotel
    id_mesta = request.forms.mesto_izbira

    
    nastanitev = request.forms.nastanitev
    st_zvezdic = request.forms.zvezdice

    ugodnosti_izbira = request.forms.getlist("ugodnosti")
    okrozja_izbira = request.forms.getlist("okrozja")
    znamenitosti_izbira = request.forms.getlist("znamenitosti")

    dodano_okrozje = request.forms.okrozje
    id_mesto_okrozje = request.forms.mesto_okrozje
    dodana_znamenitost = request.forms.znamenitost
    id_mesto_znamenitost = request.forms.mesto_znamenitost

    if drzava:


        cur.execute("SELECT 1 FROM drzava WHERE ime_drzave=%s", [drzava])
        if cur.fetchone():
            # Uporabnik že obstaja
            return template("admin.html",
                               username=username,admini = admini,
                               napaka1='Ta država je že vnešena.',
                               napaka2 = None,
                               napaka3 = None,
                               celine = celine, drzave = drzave, mesta = mesta, ugodnosti  = ugodnosti,
                               napaka_o = None, napaka_z = None,
                            okrozja_po_mestih = okrozja_po_mestih, znamenitosti_po_mestih   = znamenitosti_po_mestih )
        else:
            cur.execute("INSERT INTO Drzava(Ime_drzave, Celina_id) VALUES (%s, %s)", [drzava, id_celine])
            return redirect("/admin/")

    elif mesto:
        cur.execute("SELECT 1 FROM mesto WHERE ime_mesta=%s", [mesto])
        if cur.fetchone():
        # Uporabnik že obstaja
            return template("admin.html",
                               username=username,admini = admini,
                               napaka1 = None,
                               napaka2='To mesto je že vnešeno.',
                               napaka3 = None,
                               celine = celine, drzave = drzave, mesta = mesta, ugodnosti  = ugodnosti,
                               napaka_o = None, napaka_z = None,
                               znamenitosti_po_mestih = znamenitosti_po_mestih, 
                            okrozja_po_mestih = okrozja_po_mestih )
        else:
            cur.execute("INSERT INTO mesto(ime_mesta, drzava_id) VALUES (%s, %s)", [mesto, id_drzave])
            return redirect("/admin/") 

    elif dodano_okrozje:
        cur.execute("SELECT * FROM lokacije JOIN mesto ON mesto.id = mesto_id WHERE mesto_id=%s AND ime_lokacije = %s", [id_mesto_okrozje, dodano_okrozje])
        if cur.fetchone():
        # Uporabnik že obstaja
            return template("admin.html",
                               username=username,admini = admini,
                               napaka1 = None,
                               napaka2= None,
                               napaka3 = None,
                               celine = celine, drzave = drzave, mesta = mesta, ugodnosti  = ugodnosti,
                               napaka_o = "To okrožje v tem mestu že obstaja", napaka_z = None,
                               znamenitosti_po_mestih = znamenitosti_po_mestih, 
                            okrozja_po_mestih = okrozja_po_mestih )
        else:
            cur.execute("INSERT INTO lokacije(ime_lokacije, tip, mesto_id) VALUES (%s, 'Okrožje',%s)", [dodano_okrozje, id_mesto_okrozje])
            return redirect("/admin/") 


    elif dodana_znamenitost:
        cur.execute("SELECT * FROM lokacije JOIN mesto ON mesto.id = mesto_id WHERE mesto_id=%s AND ime_lokacije = %s", [id_mesto_znamenitost, dodana_znamenitost ])
        if cur.fetchone():
        # Uporabnik že obstaja
            return template("admin.html",
                               username=username,admini = admini,
                               napaka1 = None,
                               napaka2= None,
                               napaka3 = None,
                               celine = celine, drzave = drzave, mesta = mesta, ugodnosti  = ugodnosti,
                               napaka_z = "Ta znamenitost v tem mestu že obstaja", napaka_o = None,
                               znamenitosti_po_mestih = znamenitosti_po_mestih, 
                            okrozja_po_mestih = okrozja_po_mestih )
        else:
            cur.execute("INSERT INTO lokacije(ime_lokacije, tip, mesto_id) VALUES (%s, 'Znamenitost',%s)", [dodana_znamenitost , id_mesto_znamenitost])
            return redirect("/admin/") 
    
    elif hotel:
        cur.execute("SELECT drzava_id FROM mesto WHERE id = %s", [id_mesta])
        drzava_id = cur.fetchone()
        drzava_id = drzava_id[0]

        cur.execute("SELECT * FROM hotel JOIN mesto ON mesto.id = mesto_id WHERE mesto_id=%s AND Ime = %s", [id_mesta, hotel])
        if cur.fetchone():
        # Uporabnik že obstaja
            return template("admin.html",
                               username=username,admini = admini,
                               napaka1 = None,
                               napaka2= None,
                               napaka3 = 'Ta hotel v tem mestu že obstaja.', napaka_o = None, napaka_z = None,
                               celine = celine, drzave = drzave, mesta = mesta, ugodnosti  = ugodnosti,
                               znamenitosti_po_mestih = znamenitosti_po_mestih, 
                            okrozja_po_mestih = okrozja_po_mestih)
        else:
            cur.execute("INSERT INTO hotel (Ime, st_zvezdic, tip_nastanitve, Drzava_id, Mesto_id) VALUES (%s, %s, %s, %s, %s)", [hotel, st_zvezdic, nastanitev, drzava_id, id_mesta])
            cur.execute("SELECT id FROM hotel WHERE id = (SELECT MAX(id) FROM hotel)")
            zadnji_hotel = cur.fetchone()
            zadnji_hotel = zadnji_hotel[0]
            for ugodnost in ugodnosti_izbira:
                cur.execute("INSERT INTO ima (hotel, ugodnost) VALUES (%s, %s)", [zadnji_hotel,ugodnost])
            for okrozje in okrozja_izbira:
                cur.execute("INSERT INTO Na_lokaciji (Hotel_id, Lokacija_id ) VALUES (%s, %s)",[zadnji_hotel,okrozje])
            for znamenitost in znamenitosti_izbira:
                cur.execute("INSERT INTO Na_lokaciji (Hotel_id, Lokacija_id ) VALUES (%s, %s)",[zadnji_hotel,znamenitost])
            return redirect("/admin/") 

       



######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080) #,reloader=True)
