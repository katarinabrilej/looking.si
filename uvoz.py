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
cur.execute("INSERT INTO Celina (Ime_celine) VALUES ('Južna Amerika')")
cur.execute("INSERT INTO Celina (Ime_celine) VALUES ('Afrika')")
cur.execute("INSERT INTO Celina (Ime_celine) VALUES ('Evropa')")
cur.execute("INSERT INTO Celina (Ime_celine) VALUES ('Avstralija')")
cur.execute("INSERT INTO Celina (Ime_celine) VALUES ('Azija')")
cur.execute("INSERT INTO Celina (Ime_celine) VALUES ('Antarktika')")

cur.execute("DROP TABLE IF EXISTS Drzava CASCADE")
cur.execute("""CREATE TABLE Drzava(Id SERIAL PRIMARY KEY, Ime_drzave TEXT, Celina_id INT, 
FOREIGN KEY(Celina_id) REFERENCES Celina(Id))""")
cur.execute("INSERT INTO Drzava (Ime_drzave, Celina_id) VALUES ('ZDA',1)")
cur.execute("INSERT INTO Drzava (Ime_drzave,Celina_id) VALUES ('Kostarika',2)")
cur.execute("INSERT INTO Drzava (Ime_drzave,Celina_id) VALUES ('Panama',2)")
cur.execute("INSERT INTO Drzava (Ime_drzave,Celina_id) VALUES ('Nemčija',4)")
cur.execute("INSERT INTO Drzava (Ime_drzave,Celina_id) VALUES ('Poljska',4)")
cur.execute("INSERT INTO Drzava (Ime_drzave,Celina_id) VALUES ('Slovenija',4)")


cur.execute("DROP TABLE IF EXISTS Mesto CASCADE")
cur.execute("""CREATE TABLE Mesto(Id SERIAL PRIMARY KEY, Ime_mesta TEXT, Drzava_id INT, 
FOREIGN KEY(Drzava_id) REFERENCES Drzava(Id))""")
cur.execute("INSERT INTO Mesto (Ime_mesta, Drzava_id) VALUES ('Los Angeles',1)")
cur.execute("INSERT INTO Mesto (Ime_mesta,Drzava_id) VALUES ('San Jose',2)")
cur.execute("INSERT INTO Mesto (Ime_mesta,Drzava_id) VALUES ('Panama City',3)")
cur.execute("INSERT INTO Mesto (Ime_mesta,Drzava_id) VALUES ('Honolulu',1)")
cur.execute("INSERT INTO Mesto (Ime_mesta,Drzava_id) VALUES ('Berlin',4)")
cur.execute("INSERT INTO Mesto (Ime_mesta,Drzava_id) VALUES ('Krakow',5)")


cur.execute("DROP TABLE IF EXISTS Lokacije CASCADE")
cur.execute("""CREATE TABLE Lokacije(Id SERIAL PRIMARY KEY, Ime_lokacije TEXT, Tip TEXT, Mesto_id INT, 
FOREIGN KEY(Mesto_id) REFERENCES Mesto(Id))""")
cur.execute("INSERT INTO Lokacije (Ime_lokacije, Tip, Mesto_id ) VALUES ('Waikiki Beach', 'Značilnost', 4)")
cur.execute("INSERT INTO Lokacije (Ime_lokacije, Tip, Mesto_id ) VALUES ('Waikiki', 'Okrožje', 4)")
cur.execute("INSERT INTO Lokacije (Ime_lokacije, Tip, Mesto_id ) VALUES ('Beverly Hills', 'Okrožje', 1)")
cur.execute("INSERT INTO Lokacije (Ime_lokacije, Tip, Mesto_id ) VALUES ('Deutscher Dom', 'Znamenitost', 5)")
cur.execute("INSERT INTO Lokacije (Ime_lokacije, Tip, Mesto_id ) VALUES ('Narodno Gledališče', 'Znamenitost', 2)")
cur.execute("INSERT INTO Lokacije (Ime_lokacije, Tip, Mesto_id ) VALUES ('Downtown', 'Okrožje', 3)")
 
cur.execute("DROP TABLE IF EXISTS Hotel CASCADE")
cur.execute("""CREATE TABLE Hotel(Id SERIAL PRIMARY KEY, Ime TEXT, st_zvezdic INT, 
tip_nastanitve TEXT, Drzava_id INT, Mesto_id INT,
FOREIGN KEY (Drzava_id) REFERENCES Drzava(Id) ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (Mesto_id) REFERENCES Mesto(Id) ON UPDATE CASCADE ON DELETE CASCADE)""")
cur.execute("INSERT INTO Hotel (Ime, st_zvezdic, tip_nastanitve, Drzava_id, Mesto_id) VALUES ('The Beverly Hills Hotel', 5, 'Hotel', 1, 1)")
cur.execute("INSERT INTO Hotel (Ime, st_zvezdic, tip_nastanitve, Drzava_id, Mesto_id) VALUES ('The Royal Hawaiian', 5, 'Hotel', 1, 4)")
cur.execute("INSERT INTO Hotel (Ime, st_zvezdic, tip_nastanitve, Drzava_id, Mesto_id) VALUES ('Grand Hotel Costa Rica', 4, 'Hotel', 2,2)")
cur.execute("INSERT INTO Hotel (Ime, st_zvezdic, tip_nastanitve, Drzava_id, Mesto_id) VALUES ('Eurostars Panama City', 5, 'Hotel', 3,3)")
cur.execute("INSERT INTO Hotel (Ime, st_zvezdic, tip_nastanitve, Drzava_id, Mesto_id) VALUES ('Hilton Berlin', 4, 'Hotel', 4, 5)")

cur.execute("DROP TABLE IF EXISTS Na_lokaciji CASCADE")
cur.execute("""CREATE TABLE Na_lokaciji(Hotel_id INT , Lokacija_id INT ,
PRIMARY KEY (Hotel_id, Lokacija_id), FOREIGN KEY (Hotel_id) REFERENCES Hotel(Id) ON UPDATE CASCADE ON DELETE CASCADE, 
FOREIGN KEY (Lokacija_id) REFERENCES Lokacije(Id) ON UPDATE CASCADE ON DELETE CASCADE)""")
cur.execute("INSERT INTO Na_lokaciji (Hotel_id, Lokacija_id ) VALUES (1,3)")
cur.execute("INSERT INTO Na_lokaciji (Hotel_id, Lokacija_id ) VALUES (2,5)")
cur.execute("INSERT INTO Na_lokaciji (Hotel_id, Lokacija_id ) VALUES (3,6)")
cur.execute("INSERT INTO Na_lokaciji (Hotel_id, Lokacija_id ) VALUES (4,1)")
cur.execute("INSERT INTO Na_lokaciji (Hotel_id, Lokacija_id ) VALUES (4,2)")
cur.execute("INSERT INTO Na_lokaciji (Hotel_id, Lokacija_id ) VALUES (5,4)")
 
cur.execute("DROP TABLE IF EXISTS Ugodnosti CASCADE")
cur.execute("CREATE TABLE Ugodnosti(Id SERIAL PRIMARY KEY, Ime_ugodnosti TEXT)")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('bazen')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('zajtrk')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('klima')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('spa center')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('fitnes')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('restavracija')")
cur.execute("INSERT INTO Ugodnosti (Ime_ugodnosti) VALUES ('parkirišče')")

cur.execute("DROP TABLE IF EXISTS Ima CASCADE")
cur.execute("""CREATE TABLE Ima(Hotel INT, Ugodnost INT , PRIMARY KEY (Hotel, Ugodnost),
FOREIGN KEY (Hotel) REFERENCES Hotel(Id) ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (Ugodnost) REFERENCES Ugodnosti(Id) ON UPDATE CASCADE ON DELETE CASCADE)""")
cur.execute("INSERT INTO Ima VALUES (1, 1)")
cur.execute("INSERT INTO Ima VALUES (1, 2)")
cur.execute("INSERT INTO Ima VALUES (1, 3)")
cur.execute("INSERT INTO Ima VALUES (1, 4)")
cur.execute("INSERT INTO Ima VALUES (1, 5)")
cur.execute("INSERT INTO Ima VALUES (1, 6)")
cur.execute("INSERT INTO Ima VALUES (1, 7)")
cur.execute("INSERT INTO Ima VALUES (2, 1)")
cur.execute("INSERT INTO Ima VALUES (2, 2)")
cur.execute("INSERT INTO Ima VALUES (2, 3)")
cur.execute("INSERT INTO Ima VALUES (2, 5)")
cur.execute("INSERT INTO Ima VALUES (2, 6)")
cur.execute("INSERT INTO Ima VALUES (3, 2)")
cur.execute("INSERT INTO Ima VALUES (3, 3)")
cur.execute("INSERT INTO Ima VALUES (3, 5)")
cur.execute("INSERT INTO Ima VALUES (3, 6)")
cur.execute("INSERT INTO Ima VALUES (4, 1)")
cur.execute("INSERT INTO Ima VALUES (4, 2)")
cur.execute("INSERT INTO Ima VALUES (4, 3)")
cur.execute("INSERT INTO Ima VALUES (4, 6)")
cur.execute("INSERT INTO Ima VALUES (5, 1)")
cur.execute("INSERT INTO Ima VALUES (5, 2)")
cur.execute("INSERT INTO Ima VALUES (5, 3)")
cur.execute("INSERT INTO Ima VALUES (5, 4)")
cur.execute("INSERT INTO Ima VALUES (5, 5)")
cur.execute("INSERT INTO Ima VALUES (5, 6)")
cur.execute("INSERT INTO Ima VALUES (5, 7)")

cur.execute("DROP TABLE IF EXISTS Uporabnik CASCADE")
cur.execute("""CREATE TABLE Uporabnik (Id SERIAL PRIMARY KEY, Ime TEXT, Priimek TEXT,
Uporabnisko_ime TEXT, Geslo TEXT, Tip TEXT)""")
cur.execute("""INSERT INTO Uporabnik (Ime, Priimek, Uporabnisko_ime, Geslo, Tip) VALUES 
('Katarina', 'Brilej', 'katybrilej', '12345', 'administrator')""")
cur.execute("""INSERT INTO Uporabnik (Ime, Priimek, Uporabnisko_ime, Geslo, Tip) VALUES 
('Eva', 'Deželak', 'evadezelak', '6789', 'administrator')""")

cur.execute("DROP TABLE IF EXISTS Oceni CASCADE")
cur.execute("""CREATE TABLE Oceni(Datum DATE, Mnenje TEXT, Vrednost INT,
Hotel INT REFERENCES Hotel(Id) ON UPDATE CASCADE ON DELETE CASCADE,
Uporabnik INT REFERENCES Uporabnik(Id) ON UPDATE CASCADE ON DELETE CASCADE, PRIMARY KEY (Uporabnik, Hotel, Datum))""")



#cur.execute("DROP TABLE IF EXISTS Slike CASCADE")
#cur.execute("CREATE TABLE Slike(Id SERIAL PRIMARY KEY, Slika BYTEA)")
#cur.execute("INSERT INTO Slike (Slika) VALUES (bytea('Slike\berlin_hotel.jpg'))")



# povezava http://baza.fmf.uni-lj.si/phppgadmin/
# poženemo strežnik na portu 8080, glej http://localhost:8000/
# run(host='localhost', port=8000)

# glej predavanja 4, viri, sqlite3test
