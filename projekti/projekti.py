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

def ask_for_story():
    while True:
        choice = input("Haluatko lukea tarinan? (kyllä/ei): ").strip().lower()
        if choice == 'kyllä':
            print("""
            *** Tervetuloa peliin! ***

            Aurinko on räjähtämässä, ja sen myötä maapallon ilmasto on alkanut kuumentua äärimmilleen. 
            Maailma on joutunut kaaokseen. Ihmiskunta kamppailee selviytymisestään.

            Sinä olet yksi onnekkaista, joka on kuullut huhun salaisesta bunkkerista, joka kestää kuumuuden. 
            Tämä bunkkeri sijaitsee jossain Suomessa, ja se sisältää kaiken tarvittavan elämiseen: ruokaa, vettä, ilmaa, ja turvallisuutta.

            Ainoa ongelma on, että aikaa on vain 5 tuntia ja polttoainetta rajallinen määrä.
            Jos haluat selviytyä, sinun on löydettävä tämä suojapaikka ennen kuin on liian myöhäistä.

            Onnea matkaan, seikkailijamme. Selviytyminen on omissa käsissäsi!
            """)
            break
        elif choice == 'ei':
            print("Hyvä on, hypätään suoraan toimintaan!")
            break
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
    return result


# En tiedä onko turha funktio, mutta siis laskee kahden lentokentän välisen etäisyyden:
def etaisyyden_lasku(current, target):
    start = get_airport_info(current)
    end = get_airport_info(target)
    return distance.distance((start['latitude_deg'], start['longitude_deg']),
                             (end['latitude_deg'], end['longitude_deg'])).km


def get_nearby_airports(lentokentat, current="EFHK"):
    current_lat, current_lng = None, None

    # Etsi nykyisen lentokentän koordinaatit
    for airport in lentokentat:
        if airport["ident"] == current:
            current_lat = airport["latitude_deg"]
            current_lng = airport["longitude_deg"]
            current_name = airport["name"]
            break

    if current_lat is None or current_lng is None:
        raise ValueError("Nykyistä lentokenttää ei löytynyt.")

    # Tulostetaan pelaajan nykyinen sijainti
    print(f"\nNykyinen sijaintisi: {current_name} ({current}), koordinaatit: {current_lat}, {current_lng}")

    etaisyydet = []
    # Laske etäisyydet muihin lentokenttiin, paitsi oma sijainti
    for details in lentokentat:
        name = details["name"]
        ident = details["ident"]
        lat = details['latitude_deg']
        lng = details['longitude_deg']

        # Skippaa nykyinen lentokenttä
        if ident == current:
            continue

        etaisyys = distance.distance((lat, lng), (current_lat, current_lng)).km
        etaisyydet.append((etaisyys, name, ident))

    # Järjestetään etäisyydet etäisyyden mukaan nousevasti
    etaisyydet.sort(key=lambda x: x[0])

    # Palautetaan viisi lähintä lentokenttää
    return etaisyydet[:5]

# Lentokenttätietojen haku
lentokentat = get_airport_info()

# Tulostetaan oma sijainti ja viisi lähintä lentokenttää
nearest_airports = get_nearby_airports(lentokentat)

# Tulostetaan viisi lähintä lentokenttää
print("\nLähimmät lentokenttävaihtoehdot:")
for airport in nearest_airports:
    print(f"Lentokenttä: {airport[1]} ({airport[2]}), Etäisyys: {airport[0]:.2f} km")

input("Valitse yksi näistä.")


#maali lentokentät
def maali_lentokentat():
    lentokentat = ['EFIV', 'EFOU', 'EFKS', 'EFKT', 'EFKE']
    valittu_kentta = random.choice(lentokentat)
    return valittu_kentta


kilsat_pelaaja = 1500


def alku():
    lentokent = "EFHK"
    return lentokent
aloitus = alku()

def sijainti(kilsat_pelaaja, icao, aika, game_id):
    sql = f'''UPDATE game SET location = %s, kilsat_pelaaja = %s, aika = %s WHERE id = %s'''
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql, (kilsat_pelaaja, icao, aika, game_id))


