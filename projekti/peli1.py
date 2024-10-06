from geopy import distance
import mysql.connector
import random


# Yhteyden muodostaminen tietokantaan
def create_database_connection():
    return mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        database='flight_game',
        user='root',
        password='kisumisu24',
        autocommit=True,
        collation='utf8mb4_general_ci'
    )


# Funktio tarinan näyttämiseksi
def show_story():
    print("""\
    *** Tervetuloa peliin! ***

    Aurinko on räjähtämässä, ja sen myötä maapallon ilmasto on alkanut kuumentua äärimmilleen. 
    Maailma on joutunut kaaokseen. Ihmiskunta kamppailee selviytymisestään.

    Sinä olet yksi onnekkaista, joka on kuullut huhun salaisesta bunkkerista, joka kestää kuumuuden. 
    Tämä bunkkeri sijaitsee jossain Suomessa, ja se sisältää kaiken tarvittavan elämiseen: ruokaa, vettä, ilmaa, ja turvallisuutta.

    Ainoa ongelma on, että aikaa on vain 5 tuntia ja polttoainetta rajallinen määrä.
    Jos haluat selviytyä, sinun on löydettävä tämä suojapaikka ennen kuin on liian myöhäistä.

    Onnea matkaan, seikkailijamme. Selviytyminen on omissa käsissäsi!
    """)


# Vakioidut turvapaikkalentokentät
turvapaikka_lentokentat = ['EFIV', 'EFOU', 'EFKS', 'EFKT', 'EFKE']


# Valitaan yksi turvapaikkakenttä
def valitse_turvapaikka():
    return random.choice(turvapaikka_lentokentat)


# Funktio lentomatkan keston laskemiseksi etäisyyden perusteella
def lentoaika(etaisyys_km):
    vakioaika_100_km = 12  # 12 minuuttia per 100 km
    lentoaika_minuutit = (etaisyys_km / 100) * vakioaika_100_km
    return lentoaika_minuutit


# Funktio lentokenttätietojen hakemiseksi
def get_airport_info(connection):
    sql = """SELECT ident, name, latitude_deg, longitude_deg 
             FROM airport 
             WHERE iso_country = 'FI' 
             AND type IN ('medium_airport', 'large_airport')"""
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


# Funktio etäisyyden laskemiseksi kahden lentokentän välillä
def etaisyyden_lasku(current, target, connection):
    start = lentokenttien_sijainti(current, connection)
    end = lentokenttien_sijainti(target, connection)
    if start and end:
        return distance.distance((start['latitude_deg'], start['longitude_deg']),
                                 (end['latitude_deg'], end['longitude_deg'])).km
    else:
        return None


# Funktio, joka palauttaa lentokentän sijainnin tietokannasta
def lentokenttien_sijainti(icao_code, connection):
    sql = f"SELECT latitude_deg, longitude_deg FROM airport WHERE ident = '{icao_code}'"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchone()
    if result:
        return {'latitude_deg': result['latitude_deg'], 'longitude_deg': result['longitude_deg']}
    else:
        return None


# Funktio viiden lähimmän lentokentän löytämiseksi
def get_nearby_airports(lentokentat, current="EFHK", visited_airports=[]):
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


    etaisyydet = []
    # Laske etäisyydet muihin lentokenttiin, jotka eivät ole käytyjä
    for details in lentokentat:
        ident = details["ident"]
        if ident == current or ident in visited_airports:
            continue

        etaisyys = distance.distance((details['latitude_deg'], details['longitude_deg']),
                                     (current_lat, current_lng)).km
        etaisyydet.append((etaisyys, details["name"], ident))

    etaisyydet.sort(key=lambda x: x[0])
    return etaisyydet[:5]


# Funktio pelaajan tietojen päivittämiseksi
def paivita_sijainti(valittu_lentokentta, etaisyys_uuteen, pelaajan_sijainti, kilsat_pelaaja, pelaajan_aika):
    # Päivitetään pelaajan sijainti
    pelaajan_sijainti = valittu_lentokentta[2]  # ICAO-koodi

    # Vähennetään polttoainetta (kilometrejä)
    kilsat_pelaaja -= etaisyys_uuteen

    # Lasketaan ja vähennetään lentoaika
    lentoaika_min = lentoaika(etaisyys_uuteen)
    pelaajan_aika -= lentoaika_min

    print(
        f"\nJäljellä olevat kilometrit: {kilsat_pelaaja:.2f} km; \nJäljellä oleva aika: {pelaajan_aika // 60:.0f} tuntia ja {pelaajan_aika % 60:.0f} minuuttia.")

    return pelaajan_sijainti, kilsat_pelaaja, pelaajan_aika


# Peli alkaa
def peli_kaynnista(connection):
    # Pelaajan aloitussijainti, jäljellä olevat kilometrit ja aika
    pelaajan_sijainti = "EFHK"  # Aloitussijainti Helsinki-Vantaa
    kilsat_pelaaja = 1500  # Polttoainetta jäljellä (kilometrejä)
    pelaajan_aika = 5 * 60  # 5 tuntia (muutetaan minuutteihin)
    visited_airports = [pelaajan_sijainti]

    # Valitaan turvapaikka
    turvapaikka = valitse_turvapaikka()

    # Lentokenttätietojen haku
    lentokentat = get_airport_info(connection)

    # Tulostetaan pelaajan aloitussijainti, käytettävä etäisyys ja aika
    print(f"\nAloitus sijainti: Helsinki-Vantaa")
    print(f"Pelaajalla on kilometrejä: {kilsat_pelaaja:.2f} km")
    print(f"Pelaajalla on aikaa: {pelaajan_aika // 60:.0f} tuntia.\n")

    while kilsat_pelaaja > 0 and pelaajan_aika > 0:
        # Tulostetaan oma sijainti ja viisi lähintä lentokenttää
        nearest_airports = get_nearby_airports(lentokentat, current=pelaajan_sijainti, visited_airports=visited_airports)

        # Tarkista, onko pelaajalla riittävästi polttoainetta lentää mihinkään lentokenttään
        if all(airport[0] > kilsat_pelaaja for airport in nearest_airports):
            print(
                f"Polttoainetta ei riitä mihinkään lentoon. Jäljellä olevat kilometrit: {kilsat_pelaaja:.2f} km. Peli päättyy häviöön.")
            break

        print("\nLähimmät lentokenttävaihtoehdot:")
        for i, airport in enumerate(nearest_airports):
            print(f"{i + 1}. Lentokenttä: {airport[1]}, Etäisyys: {airport[0]:.2f} km")

        # Pelaaja valitsee uuden lentokentän
        try:
            valinta = int(input("Valitse yksi lentokenttä (1-5): ")) - 1
            if valinta < 0 or valinta >= len(nearest_airports):
                raise ValueError("Väärä syöttö yritä uudelleen")
        except ValueError:
            print("Väärä syöttö yritä uudelleen.")
            continue

        # Haetaan valittu lentokenttä ja sen etäisyys
        valittu_lentokentta = nearest_airports[valinta]
        etaisyys_uuteen = valittu_lentokentta[0]

        # Tarkista, riittääkö pelaajan polttoaine lentoon
        if etaisyys_uuteen > kilsat_pelaaja:
            print(
                f"Polttoaine ei riitä lentoon tähän kohteeseen. Jäljellä olevat kilometrit: {kilsat_pelaaja:.2f} km. Yritä uudelleen.")
            continue

        # Päivitetään pelaajan sijainti ja tilanne
        pelaajan_sijainti, kilsat_pelaaja, pelaajan_aika = paivita_sijainti(valittu_lentokentta, etaisyys_uuteen,
                                                                            pelaajan_sijainti, kilsat_pelaaja,
                                                                            pelaajan_aika)
        visited_airports.append(pelaajan_sijainti)

        # Tarkista, onko pelaaja saavuttanut turvapaikan
        if pelaajan_sijainti == turvapaikka:
            print(f"Onneksi olkoon! Löysit turvapaikan {turvapaikka} ja voitit pelin!")
            break

    if pelaajan_aika <= 0:
        print("Aika loppui. Peli päättyy häviöön.")


# Pääohjelma
if __name__ == "__main__":
    connection = create_database_connection()

    # Kysy pelaajalta, haluaako hän lukea tarinan
    haluaako_lukea = input("Haluatko lukea tarinan ennen peliä? (Kyllä/Ei): ").strip().lower()
    if haluaako_lukea == "kyllä":
        show_story()
    elif haluaako_lukea == "ei":
        print("Hyvä on, hypätään suoraan toimintaan!")
    else:
        print("Virheellinen syöte. Aloitetaan peli ilman tarinaa")

    peli_kaynnista(connection)
    
    
