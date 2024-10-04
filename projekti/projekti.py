from geopy import distance
import random
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    port="3306",
    database="flight_game",
    user="matveib",
    password="salasana",
    autocommit=True,
    collation='utf8mb4_general_ci'
)

#Sijainti
def lentokenttien_sijainti(icao_code):
    sql = f"SELECT lantitude_deg, longitude_deg FROM airport WHERE ident = '{icao_code}'"
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    if result:
        return {'lantitude_deg': result[0], 'longitude_deg': result[1]}
    else:
        return None
#maali lentokentät
def maali_lentokentat():
    lentokentat = ['EFIV', 'EFOU', 'EFKS', 'EFKT', 'EFKE']
    valittu_kentta = random.choice(lentokentat)
    return valittu_kentta
