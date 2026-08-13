import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import urllib.parse

st.set_page_config(page_title="Therapie-Fahrplan", page_icon="🚗")

st.title("🚗 Therapie-Fahrplan")
st.write("Verteile die Fahrer und generiere direkte Google Maps Navi-Links!")

# --- 1. GEODATEN FUNKTION ---
@st.cache_data
def get_coordinates(ort):
    geolocator = Nominatim(user_agent="therapie_fahrplan_ebermannstadt")
    try:
        location = geolocator.geocode(f"{ort}, Bayern, Deutschland")
        if location:
            return (location.latitude, location.longitude)
        return None
    except:
        return None

# --- 2. GÄSTE-LOGIK ---
if 'gaeste' not in st.session_state:
    st.session_state.gaeste = {}

feste_gruppe = {
    "Jona": "Wiesenthau",
    "Till": "Wannbach",
    "Felix": "Unterzaunsbach",
    "Valentin": "Ebermannstadt",
    "Tim": "Dürrbrunn",
    "Jonas": "Kleingesee",
    "Moritz Taglauer": "Kanndorf",
    "Moritz Burkhard": "Gasseldorf",
    "Andreas": "Türkelstein"
}

st.header("👥 Einmalige Gäste")
col1, col2 = st.columns(2)
neuer_gast_name = col1.text_input("Name des Gastes:")
neuer_gast_ort = col2.text_input("Wohnort (z.B. Forchheim):")

if st.button("Gast hinzufügen"):
    if neuer_gast_name and neuer_gast_ort:
        st.session_state.gaeste[neuer_gast_name] = neuer_gast_ort
        st.success(f"{neuer_gast_name} aus {neuer_gast_ort} wurde hinzugefügt!")
    else:
        st.warning("Bitte Name und Wohnort eingeben.")

alle_personen = {**feste_gruppe, **st.session_state.gaeste}
alle_namen = list(alle_personen.keys())

st.divider()

# --- 3. ZIEL & AUSWAHL ---
st.header("🎯 Wo geht's hin?")
ziel = st.text_input("Zieladresse (z.B. Cinecittà Nürnberg oder Ebermannstadt):", "Nürnberg")

st.header("1. Wer fährt heute?")
fahrer = st.multiselect(
    "Fahrer auswählen:", 
    alle_namen, 
    format_func=lambda x: f"{x} ({alle_personen[x]})"
)

st.header("2. Wer muss abgeholt werden?")
mitfahrer_optionen = [person for person in alle_namen if person not in fahrer]
mitfahrer = st.multiselect(
    "Mitfahrer auswählen:", 
    mitfahrer_optionen,
    format_func=lambda x: f"{x} ({alle_personen[x]})"
)

st.divider() 

# --- 4. ROUTEN BERECHNEN ---
if st.button("🚗 Routen & Aufteilung berechnen"):
    if not fahrer:
        st.error("Bitte wähle mindestens einen Fahrer aus!")
    elif not ziel:
        st.error("Bitte gib ein Ziel ein!")
    else:
        st.info("Berechne die optimalen Zuteilungen...")
        
        # Koordinaten für alle abrufen
        fahrer_coords = {f: get_coordinates(alle_personen[f]) for f in fahrer}
        mitfahrer_coords = {m: get_coordinates(alle_personen[m]) for m in mitfahrer}
        
        # Aufteilung: Jeder Mitfahrer sucht sich den Fahrer, der ihm am nächsten ist
        aufteilung = {f: [] for f in fahrer}
        
        for m, m_coord in mitfahrer_coords.items():
            if not m_coord:
                st.warning(f"Ort für {m} ({alle_personen[m]}) nicht gefunden!")
                continue
                
            # Finde den nächsten Fahrer
            naechster_fahrer = None
            min_distanz = float('inf')
            
            for f, f_coord in fahrer_coords.items():
                if f_coord:
                    distanz = geodesic(f_coord, m_coord).km
                    if distanz < min_distanz:
                        min_distanz = distanz
                        naechster_fahrer = f
                        
            if naechster_fahrer:
                aufteilung[naechster_fahrer].append(m)

        # Routen sortieren und Links generieren
        st.success("Hier sind die fertigen Fahrpläne!")
        
        for f in fahrer:
            st.subheader(f"🚘 Auto von {f}")
            f_ort = alle_personen[f]
            zugewiesene_mitfahrer = aufteilung[f]
            
            if not zugewiesene_mitfahrer:
                st.write("Fährt direkt zum Ziel (keine Mitfahrer).")
                # Link ohne Wegpunkte
                url_origin = urllib.parse.quote(f"{f_ort}, Bayern, Deutschland")
                url_dest = urllib.parse.quote(ziel)
                gmaps_link = f"https://www.google.com/maps/dir/?api=1&origin={url_origin}&destination={url_dest}"
                st.markdown(f"[📍 Google Maps Route für {f} öffnen]({gmaps_link})")
            
            else:
                # Wegpunkte nach Entfernung vom Fahrer sortieren (damit er nicht hin und her fährt)
                f_coord = fahrer_coords[f]
                sortierte_mitfahrer = []
                unbesucht = zugewiesene_mitfahrer.copy()
                aktueller_standort = f_coord
                
                while unbesucht:
                    # Suche den nächsten Mitfahrer vom aktuellen Standort aus
                    naechster = min(unbesucht, key=lambda x: geodesic(aktueller_standort, mitfahrer_coords[x]).km)
                    sortierte_mitfahrer.append(naechster)
                    aktueller_standort = mitfahrer_coords[naechster]
                    unbesucht.remove(naechster)
                
                # Mitfahrer anzeigen
                st.write("**Mitfahrer (in Abhol-Reihenfolge):**")
                for i, m in enumerate(sortierte_mitfahrer):
                    st.write(f"{i+1}. {m} ({alle_personen[m]})")
                
                # Google Maps Link zusammenbauen
                url_origin = urllib.parse.quote(f"{f_ort}, Bayern, Deutschland")
                url_dest = urllib.parse.quote(ziel)
                
                wegpunkte = []
                for m in sortierte_mitfahrer:
                    wegpunkte.append(urllib.parse.quote(f"{alle_personen[m]}, Bayern, Deutschland"))
                url_waypoints = "|".join(wegpunkte)
                
                gmaps_link = f"https://www.google.com/maps/dir/?api=1&origin={url_origin}&destination={url_dest}&waypoints={url_waypoints}"
                
                st.markdown(f"**[📍 Google Maps Route für {f} öffnen]({gmaps_link})**")
            
            st.write("---")