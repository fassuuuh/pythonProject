from geopy import distance
import mysql.connector
import random
connection = mysql.connector.connect(
         host='127.0.0.1',
         port= 3306,
         database='flight_game',
         user='root',
         password='salasana',
         autocommit=True,
         collation='utf8mb4_general_ci'
         )

def show_story():
    story = """
        *** Tervetuloa peliin! ***

        Aurinko on räjähtämässä, ja sen myötä maapallon ilmasto on alkanut kuumentua äärimmilleen. 
        Maailma on joutunut kaaokseen. Ihmiskunta kamppailee selviytymisestään.

        Sinä olet yksi onnekkaista, joka on kuullut huhun salaisesta bunkkerista, joka kestää kuumuuden. 
        Tämä bunkkeri sijaitsee jossain Suomessa, ja se sisältää kaiken tarvittavan elämiseen: ruokaa, vettä, ilmaa, ja turvallisuutta.

        Ainoa ongelma on, että aikaa on vain 5 tuntia ja polttoainetta rajallinen määrä.
        Jos haluat selviytyä, sinun on löydettävä tämä suojapaikka ennen kuin on liian myöhäistä.

        Onnea matkaan, seikkailijamme. Selviytyminen on omissa käsissäsi!
        """
    print(story)


# Funktio, joka kysyy pelaajalta haluaako hän lukea tarinan
def ask_for_story():
    choice = input("Haluatko lukea tarinan? (kyllä/ei): ").strip().lower()
    if choice == 'kyllä':
        show_story()
    elif choice == 'ei':
        print("Hyvä on, hypätään suoraan toimintaan!")
    else:
        print("Virheellinen valinta. Kirjoita 'kyllä' tai 'ei'.")

ask_for_story()

def lentoaika(etaisyys_km):
    vakioaika_100_km = 12
    lentoaika_minuutit = (etaisyys_km / 100) * vakioaika_100_km

    tunnit = int(lentoaika_minuutit // 60)
    minuutit = int(lentoaika_minuutit % 60)
    return tunnit, minuutit

etaisyys = 700
tunnit, minuutit = lentoaika(etaisyys)
print(f"Lentoaika {etaisyys} km matkalle on noin {tunnit} tuntia ja {minuutit} minuuttia.")


# Lasketaan etäisyys lentokenttien välillä

def get_airport_info():
    sql = f"SELECT ident, name, latitude_deg, longitude_deg FROM airport WHERE iso_country = 'FI' and type IN ('medium_airport', 'large_airport')"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    print(result[0]["name"])
    return result

def etaisyyden_lasku(current, target):
    start = get_airport_info(current)
    end = get_airport_info(target)
    return distance.distance((start['latitude_deg'], start['longitude_deg']),
                             (end['latitude_deg'], end['longitude_deg'])).km


def get_nearby_airports(lentokentat, current = "EFHK"):
    for airport in lentokentat:
        #print(airport["ident"])
        if airport["ident"] == current:
            current_lat = airport["latitude_deg"]
            current_lng = airport["longitude_deg"]
            #print("IF")
            break

    for details in lentokentat:
        name = details["name"]
        lat = details['latitude_deg']
        lng = details['longitude_deg']
        #print(name, lat, lng, current_lat, current_lng)

        etaisyys = distance.distance((lat, lng), (current_lat, current_lng)).km

        if etaisyys < 200:
            print("less than 50 km")

def sijainti(kilsat_pelaaja, icao, aika, game_id):
    sql = f"UPDATE game SET location = %s, kilsat_pelaaja = %s, aika = %s WHERE id = %s"
    cursor = connection.cursor()
    cursor.execute(sql, (kilsat_pelaaja, icao, aika, game_id))


# etaisyyden_lasku()

lentokentat = get_airport_info()
get_nearby_airports( lentokentat)


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
