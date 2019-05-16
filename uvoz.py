#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki



# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

cur.execute("DROP TABLE IF EXISTS Podrocje CASCADE")
cur.execute("CREATE TABLE Podrocje(Id INT PRIMARY KEY, Drzava TEXT, "
"Celina TEXT)")

cur.execute("DROP TABLE IF EXISTS Ugodnosti CASCADE")
cur.execute("CREATE TABLE Ugodnosti(Id INT PRIMARY KEY, Ime_ugodnosti TEXT)")

cur.execute("DROP TABLE IF EXISTS Znacilnosti CASCADE")
cur.execute("CREATE TABLE Znacilnosti(Id INT PRIMARY KEY, Ime_znacilnosti TEXT)")

# kako dodaš hotelu več ugodnosti ko ga vnašaš?
# kako je s temi značilnostmi? pač da jih lahko dodaš več ko vnašaš neko lokacijo
# še ena stvar... pač ti maš morda lahko hotele v istem mestu, ampak ma lahko specifična lokacije druge lastnosti?
# recimo ane če iščeč hotel v ljubljani, eni bodo v središču mesta, eni pa ne bodo, sam vsi bodo pa v ljubljani,
# torej ne more met ljubljana lastnosti, da je v centru?
# vprašaj prosiiim :)

cur.execute("DROP TABLE IF EXISTS Lokacija CASCADE")
cur.execute("CREATE TABLE Lokacija(Id INT PRIMARY KEY, Ime TEXT,"
"Podrocje INT REFERENCES Podrocje(Id) ON UPDATE CASCADE ON DELETE CASCADE,"
"Znacilnost INT REFERENCES Znacilnosti(Id) ON UPDATE CASCADE ON DELETE SET NULL)")

cur.execute("DROP TABLE IF EXISTS Hotel CASCADE")
cur.execute("CREATE TABLE Hotel(Id INT PRIMARY KEY, Ime TEXT, st_zvezdic INT, "
"tip_nastanitve TEXT, kapaciteta INT,"
"Ugodnost INT REFERENCES Ugodnosti(Id) ON UPDATE CASCADE ON DELETE SET NULL,"
"Lokacija INT REFERENCES Lokacija(Id) ON UPDATE CASCADE ON DELETE CASCADE)")




# ja ta ocena in uporabnik je mal sumljivo
# pač kako se bo to sploh vnašalo??
# ocena je najbrž določena z uporabnikom, hotelom ki se oceni in datumom? ker nekdo lahko en  hotel oceni večkrat
# pa pol ja uglavnem to je treba zrihtat

cur.execute("DROP TABLE IF EXISTS Uporabnik CASCADE")
cur.execute("CREATE TABLE Uporabnik (Id INT PRIMARY KEY, Ime TEXT, Priimek TEXT,"
"Uporabnisko_ime TEXT, geslo TEXT)")

cur.execute("DROP TABLE IF EXISTS Oceni CASCADE")
cur.execute("CREATE TABLE Oceni(Datum INT, Mnenje TEXT, Vrednost DATE,"
"Hotel INT REFERENCES Hotel(Id) ON UPDATE CASCADE ON DELETE CASCADE,"
"Uporabnik INT REFERENCES Uporabnik(Id) ON UPDATE CASCADE ON DELETE CASCADE, PRIMARY KEY (Uporabnik, Hotel, Datum))")





# poženemo strežnik na portu 8080, glej http://localhost:8000/
# run(host='localhost', port=8000)

# glej predavanja 4, viri, sqlite3test
