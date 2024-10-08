from geopy import distance
import mysql.connector
import random

# MySQL-yhteys
connection = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='flight_game',
    user='root',
    password='salasana',
    autocommit=True,
    collation='utf8mb4_general_ci'
)

# Tarina
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
    while True:
        choice = input("Haluatko lukea tarinan? (kyllä/ei): ").strip().lower()
        if choice == 'kyllä':
            show_story()
            break
        elif choice == 'ei':
            print("Hyvä on, hypätään suoraan toimintaan!")
            break
        else:
            print("Virheellinen valinta. Kirjoita 'kyllä' tai 'ei'.")

# Kysytään pelaajalta haluaako tarinan
ask_for_story()

# Lentoaika laskeminen
def lentoaika(etaisyys_km):
    vakioaika_100_km = 20
    lentoaika_minuutit = (etaisyys_km / 100) * vakioaika_100_km
    tunnit = int(lentoaika_minuutit // 60)
    minuutit = int(lentoaika_minuutit % 60)
    return tunnit, minuutit

# Lentokenttien tietojen hakeminen
def get_airport_info():
    sql = "SELECT ident, name, latitude_deg, longitude_deg FROM airport WHERE iso_country = 'FI' and type IN ('medium_airport', 'large_airport')"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# Etäisyyden laskeminen kahden koordinaatin välillä
def etaisyyden_lasku(start_coords, end_coords):
    return distance.distance(start_coords, end_coords).km

# Satunnaisen maalikentän valinta
def maali_lentokentat():
    lentokentat = ['EFIV', 'EFOU', 'EFKS', 'EFKT', 'EFKE']
    valittu_kentta = random.choice(lentokentat)
    return valittu_kentta

# Tarjoa viisi lähintä lentokenttää
def get_nearby_airports(lentokentat, current, visited, remaining_time, kilsat_pelaaja):
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
    print(f"Nykyinen sijaintisi: {current_name}")

    etaisyydet = []
    # Laske etäisyydet muihin lentokenttiin, paitsi jo käydyt kentät
    for details in lentokentat:
        name = details["name"]
        ident = details["ident"]
        lat = details['latitude_deg']
        lng = details['longitude_deg']

        # Skippaa nykyinen lentokenttä ja jo käydyt kentät
        if ident == current or ident in visited:
            continue

        etaisyys = etaisyyden_lasku((current_lat, current_lng), (lat, lng))
        tunnit, minuutit = lentoaika(etaisyys)
        matka_aika = tunnit * 60 + minuutit

        if matka_aika <= remaining_time and etaisyys <= kilsat_pelaaja:
            etaisyydet.append((etaisyys, name, ident, matka_aika))

    # Järjestetään etäisyydet etäisyyden mukaan nousevasti
    etaisyydet.sort(key=lambda x: x[0])

    # Palautetaan viisi lähintä lentokenttää
    return etaisyydet[:5]


# Pääpelisilmukka
def peli():
    lentokentat = get_airport_info()
    current_airport = "EFHK"  # Aloituskenttä
    visited_airports = [current_airport]  # Lista käydyistä lentokentistä
    remaining_time = 5 * 60  # Aika minuuteissa (5 tuntia)
    kilsat_pelaaja = 2000
    maali = maali_lentokentat()

    print(f"\nTehtäväsi on löytää salainen bunkkeri lentokentältä Suomessa. Etsi se ennen kuin aika tai polttoaine loppuu!")

    while remaining_time > 0 and kilsat_pelaaja > 0:
        # Näytetään pelaajalle viisi lähintä lentokenttää
        nearby_airports = get_nearby_airports(lentokentat, current_airport, visited_airports, remaining_time, kilsat_pelaaja)

        if not nearby_airports:
            print("Ei ole enään lentokenttiä joihin voit lentää\nPeli päättyi!")
            break

        print("\nLähimmät lentokenttävaihtoehdot:")
        for i, airport in enumerate(nearby_airports):
            print(f"{i + 1}. Lentokenttä: {airport[1]}, etäisyys: {airport[0]:.0f} km")

        # Pelaajan valinta (tarkistetaan, että syöte on numero ja sallituissa rajoissa)
        while True:
            try:
                valinta = int(input(f"Valitse lentokenttä minne haluat lentää (1-{i + 1}): ")) - 1
                if 0 <= valinta < len(nearby_airports):
                    break
                else:
                    print(f"Virheellinen valinta, valitse 1-{i + 1}.")
            except ValueError:
                print("Syötä numero 1-5.")

        # Valittu lentokenttä
        valittu_lentokentta = nearby_airports[valinta]
        etaisyys_uuteen = valittu_lentokentta[0]
        matka_aika = valittu_lentokentta[3]

        # Lasketaan lentoaika
        tunnit, minuutit = lentoaika(etaisyys_uuteen)

        # Päivitetään jäljellä oleva aika
        matka_aika = tunnit * 60 + minuutit
        remaining_time -= matka_aika
        kilsat_pelaaja -= etaisyys_uuteen

        if remaining_time <= 0:
            print("Aika loppui! Et ehtinyt suojapaikkaan ajoissa.")
            break

        if kilsat_pelaaja <= 0:
            print("Kilometrit loppuivat! Et ehtinyt suojapaikkaan ajoissa.")
            break

        # Päivitetään pelaajan sijainti ja käydyt lentokentät
        current_airport = valittu_lentokentta[2]
        visited_airports.append(current_airport)

        print(f"\nLennät lentokentälle {valittu_lentokentta[1]}, lentoaika: {tunnit} tuntia ja {minuutit} minuuttia.")
        print(f"\nAikaa jäljellä: {remaining_time // 60} tuntia ja {remaining_time % 60} minuuttia.")
        print(f"Kilometrejä jäljellä: {kilsat_pelaaja:.2f} km.")

        # Tarkistetaan, onko pelaaja saapunut maalikenttään
        if current_airport == maali:
            print(f"Onneksi olkoon! Saavuit maalikentälle {maali}. Voitit pelin ja löysit suojapaikan!")
            break

peli()


#Sijainti
def lentokenttien_sijainti(icao_code):
    sql = f"SELECT latitude_deg, longitude_deg FROM airport WHERE ident = '{icao_code}'"
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    if result:
        return {'latitude_deg': result[0], 'longitude_deg': result[1]}
    else:
        return None

def airport_select():
    sql = """SELECT iso_country, ident, name, latitude_deg, longitude_deg
    FROM airport
    WHERE iso_country='FI'
    AND type IN ('medium_airport', 'large_airport')
    ORDER by RAND()
    ;"""
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


kilsat_pelaaja = 1500


def alku():
    lentokent = "EFHK"
    return lentokent
aloitus = alku()


def sijainti(kilsat_pelaaja, icao, aika, game_id):
    sql = f'''UPDATE game SET location = %s, kilsat_pelaaja = %s, aika = %s WHERE id = %s'''
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql, (kilsat_pelaaja, icao, aika, game_id))
    


def sijainti(kilsat_pelaaja, icao, aika, game_id):
    sql = f'''UPDATE game SET location = %s, kilsat_pelaaja = %s, aika = %s WHERE id = %s'''
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql, (kilsat_pelaaja, icao, aika, game_id))

