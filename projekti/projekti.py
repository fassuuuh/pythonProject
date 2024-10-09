from geopy import distance
import mysql.connector
import random
import pyfiglet
from colorama import init, Fore, Style
init()

connection = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='flight_game',
    user='root',
    password='salasana',
    autocommit=True,
    collation='utf8mb4_general_ci')

text = "\nSolar Escape"
large_text = pyfiglet.figlet_format(text)
width = 150
for line in large_text.splitlines():
    print(line.center(width))

def voitto_viesti():
    text = "\nVoitto!"
    large_text = pyfiglet.figlet_format(text)
    width = 150
    for line in large_text.splitlines():
        print(line.center(width))

def havio_viesti():
    text = "\nHäviö!"
    large_text = pyfiglet.figlet_format(text)
    width = 150
    for line in large_text.splitlines():
        print(line.center(width))

def show_story(): # Taustatarina
    story = """
    *** Tervetuloa Solar Escape -peliin! ***

    Aurinko on räjähtämässä, ja sen myötä maapallon ilmasto on alkanut kuumentua äärimmilleen. 
    Maailma on joutunut kaaokseen. Ihmiskunta kamppailee selviytymisestään.

    Sinä olet yksi onnekkaista, joka on kuullut huhun salaisesta bunkkerista, joka kestää kuumuuden. 
    Tämä bunkkeri sijaitsee lentokentällä Suomen pohjois-osissa, ja se sisältää kaiken tarvittavan elämiseen: ruokaa, vettä, ilmaa, ja turvallisuutta.

    Ainoa ongelma on, että aikaa ja polttoainetta on vain rajallinen määrä.
    Jos haluat selviytyä, sinun on löydettävä tämä suojapaikka ennen kuin on liian myöhäistä.

    Onnea matkaan, seikkailijamme. Selviytyminen on omissa käsissäsi!
    """
    while True:
        choice = input("\nHaluatko lukea tarinan? (kyllä/ei): ").strip().lower()
        if choice == 'kyllä':
            print(story)
            break
        elif choice == 'ei':
            print("Hyvä on, hypätään suoraan toimintaan!")
            break
        else:
            print("Virheellinen valinta. Kirjoita 'kyllä' tai 'ei'.")



def lentoaika(etaisyys_km): # Laskee lentoajan etäisyyden perusteella
    vakioaika_100_km = 15
    lentoaika_minuutit = (etaisyys_km / 100) * vakioaika_100_km
    tunnit = int(lentoaika_minuutit // 60)
    minuutit = int(lentoaika_minuutit % 60)
    return tunnit, minuutit


def get_airport_info(): # Hakee tietokannasta tietoa Suomen lentokentistä
    sql = "SELECT ident, name, latitude_deg, longitude_deg FROM airport WHERE iso_country = 'FI' and type IN ('medium_airport', 'large_airport')"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result


def etaisyyden_lasku(start_coords, end_coords): # Laskee etäisyyden kahden sijainnin välillä
    return distance.distance(start_coords, end_coords).km

def update_wins(player_name, time_used): # Päivittää tietokantaan tiedon pelitilastoista
    cursor = connection.cursor()
    time_hours = time_used // 60
    time_minutes = time_used % 60
    time_str = f"{time_hours}:{time_minutes:02d}"
    update_sql = "UPDATE player_stats SET wins = wins + 1, time_used = %s WHERE player_name = %s"
    cursor.execute(update_sql, (time_str, player_name))
    connection.commit()
    cursor.close()


def update_losses(player_name): # Päivittää tietokantaan tiedon häviöistä
    cursor = connection.cursor()
    update_sql = "UPDATE player_stats SET losses = losses + 1 WHERE player_name = %s"
    cursor.execute(update_sql, (player_name,))
    connection.commit()
    cursor.close()

def update_distance_traveled(player_name, distance_traveled): # Päivittää tietokantaan tiedon kuljetusta etäisyydestä
    cursor = connection.cursor()
    sql_query = "UPDATE player_stats SET distance_traveled = %s WHERE player_name = %s"
    cursor.execute(sql_query, (distance_traveled, player_name))
    connection.commit()
    cursor.close()


def kysy_tilastot(): # Hakee tietokannasta ja näyttää pelitilastot pelaajan halutessa
    while True:
        vastaus = input(Fore.BLUE + "\nHaluatko nähdä tilastoja pelistä?" + Style.RESET_ALL + " (kyllä/ei): " ).strip().lower()
        if vastaus == 'kyllä':
            cursor = connection.cursor()
            sql_query = "SELECT wins, losses, num_airports_visited, distance_traveled FROM player_stats WHERE player_name = %s"
            cursor.execute(sql_query, (player_name,))
            tulos = cursor.fetchone()
            cursor.close()
            if tulos:
                wins, losses, airports_visited, distance_traveled = tulos
                print(f"\nVoittojen kokonaismäärä: {wins}")
                print(f"Häviöiden kokonaismäärä: {losses}")
                print(f"Vierailtujen lentokenttien määrä pelissä: {airports_visited}")
                print(f"Pelin aikana kuljettu kilometrimäärä: {distance_traveled:.0f}")
                break
            else:
                print(f"Ei tilastoja pelaajalle {player_name}.")
        elif vastaus == "ei":
                print("Tilastoja ei näytetä.")
                break
        else:
            print("Virheellinen vastaus. Anna 'kyllä' tai 'ei'.")


def kysy_aika_tilasto(): # Hakee tietokannasta tiedon kulutetusta ajasta pelin voittoon
    cursor = connection.cursor()
    sql_query = "SELECT time_used FROM player_stats WHERE player_name = %s"
    cursor.execute(sql_query, (player_name,))
    tulos = cursor.fetchone()
    if tulos:
        time_used = tulos
        time_str = time_used[0]
        print(f"Aika käytetty voittamiseen (hh:mm) : {time_str}")
        cursor.close()

def maali_lentokentat(): # Valitsee satunnaisesti yhden turvapaikan viidestä lentokentästä
    lentokentat = ['EFIV', 'EFOU', 'EFKS', 'EFKT', 'EFKE']
    valittu_kentta = random.choice(lentokentat)
    return valittu_kentta

def get_nearby_airports(lentokentat, current, visited, remaining_time, kilsat_pelaaja):
    # Laskee lähimmät lentokentät sijainnin perusteella ja suodattaa pois käydyt lentokentät
    current_lat, current_lng = None, None
    for airport in lentokentat:
        if airport["ident"] == current:
            current_lat = airport["latitude_deg"]
            current_lng = airport["longitude_deg"]
            current_name = airport["name"]
            break
    if current_lat is None or current_lng is None:
        raise ValueError("Nykyistä lentokenttää ei löytynyt.")

    etaisyydet = []
    for details in lentokentat:
        name = details["name"]
        ident = details["ident"]
        lat = details['latitude_deg']
        lng = details['longitude_deg']
        if ident == current or ident in visited:
            continue
        etaisyys = etaisyyden_lasku((current_lat, current_lng), (lat, lng))
        tunnit, minuutit = lentoaika(etaisyys)
        matka_aika = tunnit * 60 + minuutit
        if matka_aika <= remaining_time and etaisyys <= kilsat_pelaaja:
            etaisyydet.append((etaisyys, name, ident, matka_aika))

    etaisyydet.sort(key=lambda x: x[0])
    return etaisyydet[:5]


def peli_normal(): # Pelin pääsilmukka normaalilla vaikeudella
    lentokentat = get_airport_info()
    current_airport = "EFHK"  # Aloituskenttä
    visited_airports = [current_airport]  # Lista käydyistä lentokentistä
    remaining_time = 5 * 60  # Aika minuuteissa (5 tuntia)
    kilsat_pelaaja = 2000
    maali = maali_lentokentat()

    print(Fore.BLUE + f"\nTervetuloa Solar Escape -peliin! Tehtäväsi on löytää salainen bunkkeri lentokentältä Suomen pohjois-osista.\nEtsi se ennen kuin aika tai polttoaine loppuu!")
    print(Style.RESET_ALL)
    print(f"Nykyinen sijaintisi: Helsinki-Vantaa Airport")
    print(f"Pelaajalla on kilometrejä: {kilsat_pelaaja} km")
    print(f"Pelaajalla on aikaa: {remaining_time // 60:.0f} tuntia")

    while remaining_time > 0 and kilsat_pelaaja > 0:
        # Näytetään pelaajalle viisi lähintä lentokenttää
        nearby_airports = get_nearby_airports(lentokentat, current_airport, visited_airports, remaining_time,
                                              kilsat_pelaaja)

        if not nearby_airports:
            distance_traveled = 2000 - kilsat_pelaaja
            update_losses(player_name)
            update_distance_traveled(player_name, distance_traveled)
            update_airport_stats(player_name, visited_airports)
            print("\nEt löytänyt turvapaikkaa, etkä pääse enää mihinkään lentokenttään!")
            havio_viesti()
            kysy_tilastot()
            break

        print(Fore.GREEN + "\nLähimmät lentokenttävaihtoehdot:" + Style.RESET_ALL)
        for i, airport in enumerate(nearby_airports):
            print(f"{i + 1}. Lentokenttä: {airport[1]}, Etäisyys: {airport[0]:.0f} km")

        # Pelaajan valinta (tarkistetaan, että syöte on numero ja sallituissa rajoissa)
        while True:
            try:
                valinta = int(input(f"Valitse lentokenttä minne haluat lentää (1-{i + 1}): ")) - 1
                if 0 <= valinta < len(nearby_airports):
                    break
                else:
                    print(f"Virheellinen valinta, valitse 1-{i + 1}.")
            except ValueError:
                print(f"Syötä numero 1-{i + 1}.")

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
            havio_viesti()
            kysy_tilastot()
            break

        if kilsat_pelaaja <= 0:
            print("Kilometrit loppuivat! Et ehtinyt suojapaikkaan ajoissa.")
            havio_viesti()
            kysy_tilastot()
            break

        # Päivitetään pelaajan sijainti ja käydyt lentokentät
        current_airport = valittu_lentokentta[2]
        visited_airports.append(current_airport)

        print(f"\nNykyinen sijaintisi: {valittu_lentokentta[1]}, Lentoaika: {tunnit} tuntia ja {minuutit} minuuttia")
        print(f"Aikaa jäljellä: {remaining_time // 60} tuntia ja {remaining_time % 60} minuuttia")
        print(f"Kilometrejä jäljellä: {kilsat_pelaaja:.0f} km")

        # Tarkistetaan, onko pelaaja saapunut maalikenttään
        if current_airport == maali:
            time_used = (5 * 60) - remaining_time
            distance_traveled = 2000 - kilsat_pelaaja
            update_wins(player_name, time_used)
            update_distance_traveled(player_name, distance_traveled)
            update_airport_stats(player_name, visited_airports)
            print(f"\nOnneksi olkoon! Löysit suojapaikan ja voitit pelin!")
            voitto_viesti()
            kysy_tilastot()
            kysy_aika_tilasto()
            break


def peli_easy(): # Pelin pääsilmukka helpolla vaikeudella
    lentokentat = get_airport_info()
    current_airport = "EFHK"
    visited_airports = [current_airport]
    remaining_time = 7 * 60
    kilsat_pelaaja = 3000
    maali = maali_lentokentat()

    print(Fore.BLUE + f"\nTervetuloa Solar Escape -peliin! Tehtäväsi on löytää salainen bunkkeri lentokentältä Suomen pohjois-osista.\nEtsi se ennen kuin aika tai polttoaine loppuu!")
    print(Style.RESET_ALL)
    print(f"Nykyinen sijaintisi: Helsinki-Vantaa Airport")
    print(f"Pelaajalla on kilometrejä: {kilsat_pelaaja} km")
    print(f"Pelaajalla on aikaa: {remaining_time // 60:.0f} tuntia")

    while remaining_time > 0 and kilsat_pelaaja > 0:
        # Näytetään pelaajalle viisi lähintä lentokenttää
        nearby_airports = get_nearby_airports(lentokentat, current_airport, visited_airports, remaining_time,
                                              kilsat_pelaaja)

        if not nearby_airports:
            distance_traveled = 3000 - kilsat_pelaaja
            update_losses(player_name)
            update_distance_traveled(player_name, distance_traveled)
            update_airport_stats(player_name, visited_airports)
            print("\nEt löytänyt turvapaikkaa, etkä pääse enää mihinkään lentokenttään!")
            havio_viesti()
            kysy_tilastot()
            break

        print(Fore.GREEN + "\nLähimmät lentokenttävaihtoehdot:" + Style.RESET_ALL)
        for i, airport in enumerate(nearby_airports):
            print(f"{i + 1}. Lentokenttä: {airport[1]}, Etäisyys: {airport[0]:.0f} km")

        # Pelaajan valinta (tarkistetaan, että syöte on numero ja sallituissa rajoissa)
        while True:
            try:
                valinta = int(input(f"Valitse lentokenttä minne haluat lentää (1-{i + 1}): ")) - 1
                if 0 <= valinta < len(nearby_airports):
                    break
                else:
                    print(f"Virheellinen valinta, valitse 1-{i + 1}")
            except ValueError:
                print(f"Syötä numero 1-{i + 1}")

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
            havio_viesti()
            kysy_tilastot()
            break

        if kilsat_pelaaja <= 0:
            print("Kilometrit loppuivat! Et ehtinyt suojapaikkaan ajoissa.")
            havio_viesti()
            kysy_tilastot()
            break

        # Päivitetään pelaajan sijainti ja käydyt lentokentät
        current_airport = valittu_lentokentta[2]
        visited_airports.append(current_airport)

        print(f"\nNykyinen sijaintisi: {valittu_lentokentta[1]}, Lentoaika: {tunnit} tuntia ja {minuutit} minuuttia")
        print(f"Aikaa jäljellä: {remaining_time // 60} tuntia ja {remaining_time % 60} minuuttia")
        print(f"Kilometrejä jäljellä: {kilsat_pelaaja:.0f} km")

        # Tarkistetaan, onko pelaaja saapunut maalikenttään
        if current_airport == maali:
            time_used = (7 * 60) - remaining_time
            distance_traveled = 3000 - kilsat_pelaaja
            update_wins(player_name, time_used)
            update_distance_traveled(player_name, distance_traveled)
            update_airport_stats(player_name, visited_airports)
            print(f"\nOnneksi olkoon! Löysit suojapaikan ja voitit pelin!")
            voitto_viesti()
            kysy_tilastot()
            kysy_aika_tilasto()
            break


def peli_hard(): # Pelin pääsilmukka vaikealla vaikeudella
    lentokentat = get_airport_info()
    current_airport = "EFHK"
    visited_airports = [current_airport]
    remaining_time = 3 * 60
    kilsat_pelaaja = 1000
    maali = maali_lentokentat()

    print(Fore.BLUE + f"\nTervetuloa Solar Escape -peliin! Tehtäväsi on löytää salainen bunkkeri lentokentältä Suomen pohjois-osista.\nEtsi se ennen kuin aika tai polttoaine loppuu!")
    print(Style.RESET_ALL)
    print(f"Nykyinen sijaintisi: Helsinki-Vantaa Airport")
    print(f"Pelaajalla on kilometrejä: {kilsat_pelaaja} km")
    print(f"Pelaajalla on aikaa: {remaining_time // 60:.0f} tuntia")

    while remaining_time > 0 and kilsat_pelaaja > 0:
        # Näytetään pelaajalle viisi lähintä lentokenttää
        nearby_airports = get_nearby_airports(lentokentat, current_airport, visited_airports, remaining_time,
                                              kilsat_pelaaja)

        if not nearby_airports:
            distance_traveled = 1000 - kilsat_pelaaja
            update_losses(player_name)
            update_distance_traveled(player_name, distance_traveled)
            update_airport_stats(player_name, visited_airports)
            print("\nEt löytänyt turvapaikkaa, etkä pääse enää mihinkään lentokenttään!")
            havio_viesti()
            kysy_tilastot()
            break

        print(Fore.GREEN + "\nLähimmät lentokenttävaihtoehdot:" + Style.RESET_ALL)
        for i, airport in enumerate(nearby_airports):
            print(f"{i + 1}. Lentokenttä: {airport[1]}, Etäisyys: {airport[0]:.0f} km")

        # Pelaajan valinta (tarkistetaan, että syöte on numero ja sallituissa rajoissa)
        while True:
            try:
                valinta = int(input(f"Valitse lentokenttä minne haluat lentää (1-{i + 1}): ")) - 1
                if 0 <= valinta < len(nearby_airports):
                    break
                else:
                    print(f"Virheellinen valinta, valitse 1-{i + 1}.")
            except ValueError:
                print(f"Syötä numero 1-{i + 1}.")

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
            havio_viesti()
            kysy_tilastot()
            break

        if kilsat_pelaaja <= 0:
            print("Kilometrit loppuivat! Et ehtinyt suojapaikkaan ajoissa.")
            havio_viesti()
            kysy_tilastot()
            break

        # Päivitetään pelaajan sijainti ja käydyt lentokentät
        current_airport = valittu_lentokentta[2]
        visited_airports.append(current_airport)

        print(f"\nNykyinen sijaintisi: {valittu_lentokentta[1]}, Lentoaika: {tunnit} tuntia ja {minuutit} minuuttia")
        print(f"Aikaa jäljellä: {remaining_time // 60} tuntia ja {remaining_time % 60} minuuttia")
        print(f"Kilometrejä jäljellä: {kilsat_pelaaja:.0f} km")

        # Tarkistetaan, onko pelaaja saapunut maalikenttään
        if current_airport == maali:
            time_used = (3 * 60) - remaining_time
            distance_traveled = 1000 - kilsat_pelaaja
            update_wins(player_name, time_used)
            update_distance_traveled(player_name, distance_traveled)
            update_airport_stats(player_name, visited_airports)
            print(f"\nOnneksi olkoon! Löysit suojapaikan ja voitit pelin!")
            voitto_viesti()
            kysy_tilastot()
            kysy_aika_tilasto()
            break

def update_airport_stats(player_name, visited_airports):
    try:
        cursor = connection.cursor()
        # Muunna lentokenttälista merkkijonoksi
        airports_visited_str = ', '.join(visited_airports)
        # Lentokenttien lukumäärä
        num_airports_visited = len(visited_airports)
        # Päivitä tiedot tietokantaan
        update_query = """UPDATE player_stats SET airports_visited = %s, num_airports_visited = %s WHERE player_name = %s"""
        cursor.execute(update_query, (airports_visited_str, num_airports_visited, player_name))
        connection.commit()
    finally:
        cursor.close()

def ask_for_gamemode():
    while True:
        peli_vaikeus = input("\nValitse pelin vaikeus: (easy/normal/hard): ").strip().lower()
        if peli_vaikeus == 'easy':
            peli_easy()
            break
        elif peli_vaikeus == 'normal':
            peli_normal()
            break
        elif peli_vaikeus == 'hard':
            peli_hard()
            break
        else:
            print("Virheellinen valinta!")

def insert_or_check_player(player_name):
    cursor = connection.cursor()
    # Check if the player already exists
    check_sql = "SELECT id FROM player_stats WHERE player_name = %s"
    cursor.execute(check_sql, (player_name,))
    player = cursor.fetchone()
    if not player:
        # Insert player if they don't exist
        insert_sql = "INSERT INTO player_stats (player_name) VALUES (%s)"
        cursor.execute(insert_sql, (player_name,))
        connection.commit()
        print(f"Tallennetaan pelaaja '{player_name}' tietokantaan.")
    else:
        print(Style.BRIGHT + f"Tervetuloa takaisin {player_name}!")
        print(Style.RESET_ALL)
        cursor.close()

while True:
    try:
        ika = int(input("Syötä ikä: "))
        if ika >= 12:
            player_name = input("Syötä nimi: ").strip().lower()
            insert_or_check_player(player_name)
            show_story()
            ask_for_gamemode()
            break
        else:
            print(Fore.RED + 'Peli ei sovellu alle 12-vuotialle. Lopetetaan peli.')
            break
    except ValueError:
        print("Virheellinen syöte! Anna numero.")

connection.close()

