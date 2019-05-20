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

cur.execute("DROP TABLE IF EXISTS Celina CASCADE")
cur.execute("CREATE TABLE Celina(Id SERIAL PRIMARY KEY, Ime_celine TEXT)")
cur.execute("INSERT INTO Celina (Ime_celine) VALUES ('Severna Amerika')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('Južna Amerika')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('Afrika')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('Evropa')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('Avstralija')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('Azija')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('Antarktika')")

cur.execute("DROP TABLE IF EXISTS Drzava CASCADE")
cur.execute("""CREATE TABLE Drzava(Id SERIAL PRIMARY KEY, Ime_drzave TEXT, Celina_id INT, 
FOREIGN KEY(Celina_id) REFERENCES Celina(Id))""")
cur.execute("INSERT INTO Drzava (Ime_drzave) VALUES ('ZDA')")
cur.execute("INSERT INTO Drzava (Ime_drzave) VALUES ('Kostarika')")
cur.execute("INSERT INTO Drzava (Ime_drzave) VALUES ('Panama')")
cur.execute("INSERT INTO Drzava (Ime_drzave) VALUES ('Nemčija')")
cur.execute("INSERT INTO Drzava (Ime_drzave) VALUES ('Poljska')")


cur.execute("DROP TABLE IF EXISTS Mesto CASCADE")
cur.execute("""CREATE TABLE Mesto(Id SERIAL PRIMARY KEY, Ime_mesta TEXT, Drzava_id INT, 
FOREIGN KEY(Drzava_id) REFERENCES Drzava(Id))""")
cur.execute("INSERT INTO Mesto (Ime_mesta) VALUES ('Los Angeles')")
cur.execute("INSERT INTO Mesto (Ime_mesta) VALUES ('San Jose')")
cur.execute("INSERT INTO Mesto (Ime_mesta) VALUES ('Panama City')")
cur.execute("INSERT INTO Mesto (Ime_mesta) VALUES ('Honolulu')")
cur.execute("INSERT INTO Mesto (Ime_mesta) VALUES ('Berlin')")
cur.execute("INSERT INTO Mesto (Ime_mesta) VALUES ('Krakow')")

# vnesi podatke 
cur.execute("DROP TABLE IF EXISTS Lokacija CASCADE")
cur.execute("""CREATE TABLE Lokacija(Id SERIAL PRIMARY KEY, Ime_lokacije TEXT, Tip TEXT, Mesto_id INT, 
FOREIGN KEY(Mesto_id) REFERENCES Mesto(Id))""")
#cur.execute("INSERT INTO Lokacija (Ime_lokacije) VALUES ('??')")
#cur.execute("INSERT INTO Znacilnosti (Ime_znacilnosti) VALUES ('smučišče')")
#cur.execute("INSERT INTO Znacilnosti (Ime_znacilnosti) VALUES ('plaža')")
#cur.execute("INSERT INTO Znacilnosti (Ime_znacilnosti) VALUES ('center mesta')")
#cur.execute("INSERT INTO Znacilnosti (Ime_znacilnosti) VALUES ('gore')")
 
cur.execute("DROP TABLE IF EXISTS Hotel CASCADE")
cur.execute("""CREATE TABLE Hotel(Id SERIAL PRIMARY KEY, Ime TEXT, st_zvezdic INT, 
tip_nastanitve TEXT, Drzava_id INT, Mesto_id INT,
FOREIGN KEY (Drzava_id) REFERENCES Drzava(Id) ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (Mesto_id) REFERENCES Mesto(Id) ON UPDATE CASCADE ON DELETE CASCADE)""")
cur.execute("INSERT INTO Hotel (Ime, st_zvezdic, tip_nastanitve) VALUES ('The Beverly Hills Hotel', 5, 'Hotel', 'ZDA', 'Los Angeles')")
cur.execute("INSERT INTO Hotel (Ime, st_zvezdic, tip_nastanitve) VALUES ('The Royal Hawaiian', 5, 'Hotel', 'ZDA', 'Honolulu')")
cur.execute("INSERT INTO Hotel (Ime, st_zvezdic, tip_nastanitve) VALUES ('Grand Hotel Costa Rica', 4, 'Hotel', 'Kostarika',San Jose')")
cur.execute("INSERT INTO Hotel (Ime, st_zvezdic, tip_nastanitve) VALUES ('Eurostars Panama City', 5, 'Hotel', 'Panama',Panama City')")
cur.execute("INSERT INTO Hotel (Ime, st_zvezdic, tip_nastanitve) VALUES ('Hilton Berlin', 4, 'Hotel', 'Nemčija', Berlin')")

# vnesi podatke 
cur.execute("DROP TABLE IF EXISTS Na_lokaciji CASCADE")
cur.execute("""CREATE TABLE Na_lokaciji(Hotel_id INT , Lokacija_id INT ,
PRIMARY KEY (Hotel_id, Lokacija_id), FOREIGN KEY (Hotel_id) REFERENCES Hotel(Id) ON UPDATE CASCADE ON DELETE CASCADE, 
FOREIGN KEY (Lokacija_id) REFERENCES Lokacija(Id) ON UPDATE CASCADE ON DELETE CASCADE)""")
 
cur.execute("DROP TABLE IF EXISTS Ugodnosti CASCADE")
cur.execute("CREATE TABLE Ugodnosti(Id SERIAL PRIMARY KEY, Ime_ugodnosti TEXT)")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('bazen')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('zajtrk')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('klima')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('spa center')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('fitnes')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('restavracija')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('parkirišče')")

# vnesi podatke 
cur.execute("DROP TABLE IF EXISTS Ima CASCADE")
cur.execute("""CREATE TABLE Ima(Hotel INT, Ugodnost INT , PRIMARY KEY (Hotel, Ugodnost),
FOREIGN KEY (Hotel) REFERENCES Hotel(Id) ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (Ugodnost) REFERENCES Ugodnosti(Id) ON UPDATE CASCADE ON DELETE CASCADE)""")
cur.execute("INSERT INTO Ima VALUES (1, 1)")
cur.execute("INSERT INTO Ima VALUES (1, 2)")

cur.execute("DROP TABLE IF EXISTS Uporabnik CASCADE")
cur.execute("""CREATE TABLE Uporabnik (Id SERIAL PRIMARY KEY, Ime TEXT, Priimek TEXT,
Uporabnisko_ime TEXT, geslo TEXT)""")

cur.execute("DROP TABLE IF EXISTS Oceni CASCADE")
cur.execute("""CREATE TABLE Oceni(Datum DATE, Mnenje TEXT, Vrednost INT,
Hotel INT REFERENCES Hotel(Id) ON UPDATE CASCADE ON DELETE CASCADE,
Uporabnik INT REFERENCES Uporabnik(Id) ON UPDATE CASCADE ON DELETE CASCADE, PRIMARY KEY (Uporabnik, Hotel, Datum))""")




# povezava http://baza.fmf.uni-lj.si/phppgadmin/
# poženemo strežnik na portu 8080, glej http://localhost:8000/
# run(host='localhost', port=8000)

# glej predavanja 4, viri, sqlite3test
