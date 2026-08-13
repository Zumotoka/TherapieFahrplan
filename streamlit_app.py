import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import urllib.parse

st.set_page_config(page_title="Therapie-Fahrplan", page_icon="🚗")

st.title("🚗 Therapie-Fahrplan")
st.write("Verteile die Fahrer intelligent, beachte die Auto-Kapazität (max. 4 Mitfahrer) und generiere direkte Navi-Links!")

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
ziel = st.text_input("Zieladresse (z.B. Cinecittà Nürnberg):", "Nürnberg")

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

# Option für Mitfahrer ohne Umweg
st.header("3. Wer steigt direkt zu? (Ohne Umweg)")
mitfahrer_ohne_umweg = st.multiselect(
    "Diese Personen belegen einen Platz im Auto, werden aber NICHT ins Navi einprogrammiert:", 
    mitfahrer, 
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
        max_kapazitaet = len(fahrer) * 4
        if len(mitfahrer) > max_kapazitaet:
            st.error(f"Achtung! Ihr habt {len(mitfahrer)} Mitfahrer, aber {len(fahrer)} Autos können maximal {max_kapazitaet} Personen mitnehmen.")
        else:
            st.info("Berechne die optimalen Zuteilungen...")
            
            fahrer_coords = {f: get_coordinates(alle_personen[f]) for f in fahrer}
            mitfahrer_coords = {m: get_coordinates(alle_personen[m]) for m in mitfahrer}
            
            aufteilung = {f: [] for f in fahrer}
            unverteilt = list(mitfahrer)
            
            distanz_liste = []
            for m in unverteilt:
                m_coord = mitfahrer_coords[m]
                if not m_coord:
                    st.warning(f"Ort für {m} nicht gefunden!")
                    unverteilt.remove(m)
                    continue
                for f in fahrer:
                    f_coord = fahrer_coords[f]
                    if f_coord:
                        dist = geodesic(f_coord, m_coord).km
                        distanz_liste.append((dist, f, m))
            
            distanz_liste.sort(key=lambda x: x[0])
            
            for dist, f, m in distanz_liste:
                if m in unverteilt and len(aufteilung[f]) < 4:
                    aufteilung[f].append(m)
                    unverteilt.remove(m)

            st.success("Hier sind die fertigen Fahrpläne!")
            
            for f in fahrer:
                st.subheader(f"🚘 Auto von {f}")
                f_ort = alle_personen[f]
                zugewiesene_mitfahrer = aufteilung[f]
                
                if not zugewiesene_mitfahrer:
                    st.write("Fährt direkt zum Ziel (keine Mitfahrer).")
                    url_origin = urllib.parse.quote(f"{f_ort}, Bayern, Deutschland")
                    url_dest = urllib.parse.quote(ziel)
                    gmaps_link = f"https://www.google.com/maps/dir/?api=1&origin={url_origin}&destination={url_dest}"
                    st.markdown(f"[📍 Google Maps Route für {f} öffnen]({gmaps_link})")
                
                else:
                    f_coord = fahrer_coords[f]
                    sortierte_mitfahrer = []
                    unbesucht = zugewiesene_mitfahrer.copy()
                    aktueller_standort = f_coord
                    
                    while unbesucht:
                        naechster = min(unbesucht, key=lambda x: geodesic(aktueller_standort, mitfahrer_coords[x]).km)
                        sortierte_mitfahrer.append(naechster)
                        aktueller_standort = mitfahrer_coords[naechster]
                        unbesucht.remove(naechster)
                    
                    st.write(f"**Mitfahrer ({len(sortierte_mitfahrer)}/4 Plätze belegt):**")
                    for i, m in enumerate(sortierte_mitfahrer):
                        zusatz = " *(steigt ohne Umweg zu)*" if m in mitfahrer_ohne_umweg else ""
                        st.write(f"{i+1}. {m} ({alle_personen[m]}){zusatz}")
                    
                    url_origin = urllib.parse.quote(f"{f_ort}, Bayern, Deutschland")
                    url_dest = urllib.parse.quote(ziel)
                    
                    # Wegpunkte bauen, aber Leute "ohne Umweg" aussortieren
                    wegpunkte = [urllib.parse.quote(f"{alle_personen[m]}, Bayern, Deutschland") 
                                 for m in sortierte_mitfahrer if m not in mitfahrer_ohne_umweg]
                    
                    if wegpunkte:
                        url_waypoints = "|".join(wegpunkte)
                        gmaps_link = f"https://www.google.com/maps/dir/?api=1&origin={url_origin}&destination={url_dest}&waypoints={url_waypoints}"
                    else:
                        gmaps_link = f"https://www.google.com/maps/dir/?api=1&origin={url_origin}&destination={url_dest}"
                    
                    st.markdown(f"**[📍 Google Maps Route für {f} öffnen]({gmaps_link})**")
                
                st.write("---")