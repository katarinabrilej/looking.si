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
cur.execute("""CREATE TABLE Podrocje(Id SERIAL PRIMARY KEY, Celina TEXT, 
Drzava TEXT, Mesto TEXT, Okrozje TEXT)""")
cur.execute("INSERT INTO Podrocje (Celina, Drzava, Mesto, Okrozje) VALUES ('Severna Amerika', 'ZDA', 'Los Angeles', 'neki')")


cur.execute("DROP TABLE IF EXISTS Ugodnosti CASCADE")
cur.execute("CREATE TABLE Ugodnosti(Id SERIAL PRIMARY KEY, Ime_ugodnosti TEXT)")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('bazen')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('zajtrk')")


cur.execute("DROP TABLE IF EXISTS Lokacija CASCADE")
cur.execute("""CREATE TABLE Lokacija(Id SERIAL PRIMARY KEY, Ime TEXT,
Podrocje INT REFERENCES Podrocje(Id) ON UPDATE CASCADE ON DELETE CASCADE)""")
cur.execute("INSERT INTO Lokacija (Ime, Podrocje) VALUES ('The Beverly Hills Hotel', 1)")


cur.execute("DROP TABLE IF EXISTS Hotel CASCADE")
cur.execute("""CREATE TABLE Hotel(Id SERIAL PRIMARY KEY, Ime TEXT, st_zvezdic INT, 
tip_nastanitve TEXT, kapaciteta INT,
Lokacija INT REFERENCES Lokacija(Id) ON UPDATE CASCADE ON DELETE CASCADE)""")
cur.execute("INSERT INTO Hotel (Ime, st_zvezdic, tip_nastanitve, kapaciteta, Lokacija) VALUES ('The Beverly Hills Hotel', 5, 'hotel', 100, 1)")


cur.execute("DROP TABLE IF EXISTS Ima CASCADE")
cur.execute("""CREATE TABLE Ima(Hotel INT REFERENCES Hotel(Id) ON UPDATE CASCADE ON DELETE CASCADE,
Ugodnost INT REFERENCES Ugodnosti(Id) ON UPDATE CASCADE ON DELETE CASCADE, PRIMARY KEY (Hotel, Ugodnost))""")
cur.execute("INSERT INTO Ima VALUES (1, 1)")
cur.execute("INSERT INTO Ima VALUES (1, 2)")


cur.execute("DROP TABLE IF EXISTS Znacilnosti CASCADE")
cur.execute("CREATE TABLE Znacilnosti(Id SERIAL PRIMARY KEY, Ime_znacilnosti TEXT)")
cur.execute("INSERT INTO Znacilnosti (Ime_znacilnosti) VALUES ('smučišče')")
cur.execute("INSERT INTO Znacilnosti (Ime_znacilnosti) VALUES ('plaža')")
cur.execute("INSERT INTO Znacilnosti (Ime_znacilnosti) VALUES ('center mesta')")
cur.execute("INSERT INTO Znacilnosti (Ime_znacilnosti) VALUES ('gore')")


cur.execute("DROP TABLE IF EXISTS Je_del CASCADE")
cur.execute("""CREATE TABLE Je_del(Lokacija INT REFERENCES Lokacija(Id) ON UPDATE CASCADE ON DELETE CASCADE,
Znacilnost INT REFERENCES Znacilnosti(Id) ON UPDATE CASCADE ON DELETE CASCADE, PRIMARY KEY (Lokacija, Znacilnost))""")
cur.execute("INSERT INTO Je_del VALUES (1, 1)")
cur.execute("INSERT INTO Je_del VALUES (1, 4)")


cur.execute("DROP TABLE IF EXISTS Uporabnik CASCADE")
cur.execute("""CREATE TABLE Uporabnik (Id SERIAL PRIMARY KEY, Ime TEXT, Priimek TEXT,
Uporabnisko_ime TEXT, geslo TEXT)""")


cur.execute("DROP TABLE IF EXISTS Oceni CASCADE")
cur.execute("""CREATE TABLE Oceni(Datum DATE, Mnenje TEXT, Vrednost INT,
Hotel INT REFERENCES Hotel(Id) ON UPDATE CASCADE ON DELETE CASCADE,
Uporabnik INT REFERENCES Uporabnik(Id) ON UPDATE CASCADE ON DELETE CASCADE, PRIMARY KEY (Uporabnik, Hotel, Datum))""")





# poženemo strežnik na portu 8080, glej http://localhost:8000/
# run(host='localhost', port=8000)

# glej predavanja 4, viri, sqlite3test
