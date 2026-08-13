import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.title("🚗 Therapie-Fahrplan")
st.write("Hier verteilen wir unsere Fahrer und berechnen die effizientesten Routen!")

# --- 1. GEODATEN FUNKTION ---
# st.cache_data sorgt dafür, dass Koordinaten gespeichert werden und die App schnell bleibt
@st.cache_data
def get_coordinates(ort):
    # Der user_agent ist quasi unser Name, mit dem wir beim Kartendienst anklopfen
    geolocator = Nominatim(user_agent="therapie_fahrplan_ebermannstadt")
    try:
        # Wir fügen Bayern hinzu, damit kleine Orte fehlerfrei gefunden werden!
        such_anfrage = f"{ort}, Bayern, Deutschland"
        location = geolocator.geocode(such_anfrage)
        if location:
            return [location.latitude, location.longitude]
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

# --- 3. AUSWAHL-MENÜS ---
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

# --- 4. KARTE & ROUTE BERECHNEN ---
if st.button("Route berechnen & Karte anzeigen"):
    if not fahrer:
        st.error("Bitte wähle mindestens einen Fahrer aus!")
    elif not mitfahrer:
        st.error("Bitte wähle mindestens einen Mitfahrer aus!")
    else:
        st.success("Orte werden auf der Karte gesucht...")
        
        # Karte erstellen und auf den Raum Ebermannstadt (grob) zentrieren
        m = folium.Map(location=[49.782, 11.186], zoom_start=11)
        
        # Alle Fahrer als GRÜNE Autos auf die Karte setzen
        for f in fahrer:
            ort = alle_personen[f]
            coords = get_coordinates(ort)
            if coords:
                folium.Marker(
                    location=coords,
                    popup=f"{f} (Fahrer aus {ort})",
                    tooltip=f,
                    icon=folium.Icon(color="green", icon="car", prefix="fa")
                ).add_to(m)
            else:
                st.warning(f"Konnte den Ort {ort} für {f} nicht finden.")
                
        # Alle Mitfahrer als BLAUE Personen auf die Karte setzen
        for m_person in mitfahrer:
            ort = alle_personen[m_person]
            coords = get_coordinates(ort)
            if coords:
                folium.Marker(
                    location=coords,
                    popup=f"{m_person} (Mitfahrer aus {ort})",
                    tooltip=m_person,
                    icon=folium.Icon(color="blue", icon="user", prefix="fa")
                ).add_to(m)
            else:
                st.warning(f"Konnte den Ort {ort} für {m_person} nicht finden.")

        # Die Karte in der App anzeigen
        st_folium(m, width=700, height=500)