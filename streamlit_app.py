import streamlit as st
import urllib.parse
import math

st.set_page_config(page_title="Therapie-Fahrplan", page_icon="🚗")

st.title("🚗 Therapie-Fahrplan (Ohne Installationen)")
st.write("Verteile Fahrer und Mitfahrer, beachte die 4er-Grenze und erhalte direkte Google-Maps-Links!")

# --- 1. Feste Koordinaten (Ungefähre GPS-Daten für die Region, ganz ohne geopy) ---
ort_koordinaten = {
    "Wiesenthau": (49.711, 11.162),
    "Wannbach": (49.742, 11.233),
    "Unterzaunsbach": (49.731, 11.205),
    "Ebermannstadt": (49.774, 11.082),
    "Dürrbrunn": (49.789, 11.192),
    "Kleingesee": (49.805, 11.312),
    "Kanndorf": (49.761, 11.121),
    "Gasseldorf": (49.791, 11.102),
    "Türkelstein": (49.691, 11.281),
    "Forchheim": (49.721, 11.058),
    "Nürnberg": (49.452, 11.076)
}

# Hilfsfunktion für Luftlinie (Haversine-Formel in purem Python)
def berechne_distanz(ort1, ort2):
    coord1 = ort_koordinaten.get(ort1, (49.774, 11.082)) # Fallback Ebermannstadt
    coord2 = ort_koordinaten.get(ort2, (49.774, 11.082))
    
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371 # Erdradius in km
    return c * r

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
col1, col2, col3 = st.columns(3)
neuer_gast_name = col1.text_input("Name:")
neuer_gast_ort = col2.text_input("Wohnort:")
gast_lat = col3.number_input("Ungefähre Breitenangabe (optional, z.B. 49.7)", value=49.7)

if st.button("Gast hinzufügen"):
    if neuer_gast_name and neuer_gast_ort:
        st.session_state.gaeste[neuer_gast_name] = neuer_gast_ort
        # Ort direkt in die Liste aufnehmen
        if neuer_gast_ort not in ort_koordinaten:
            ort_koordinaten[neuer_gast_ort] = (gast_lat, 11.1)
        st.success(f"{neuer_gast_name} aus {neuer_gast_ort} hinzugefügt!")
    else:
        st.warning("Bitte Name und Wohnort eingeben.")

alle_personen = {**feste_gruppe, **st.session_state.gaeste}
alle_namen = list(alle_personen.keys())

st.divider()

# --- 3. ZIEL & AUSWAHL ---
st.header("🎯 Wo geht's hin?")
ziel = st.text_input("Zieladresse / Ort:", "Nürnberg")

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

st.header("3. Wer steigt direkt zu? (Ohne Umweg)")
mitfahrer_ohne_umweg = st.multiselect(
    "Diese Personen belegen einen Platz, werden aber im Navi ignoriert:", 
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
            aufteilung = {f: [] for f in fahrer}
            unverteilt = list(mitfahrer)
            
            # Distanzen berechnen und sortieren
            distanz_liste = []
            for m in unverteilt:
                m_ort = alle_personen[m]
                for f in fahrer:
                    f_ort = alle_personen[f]
                    dist = berechne_distanz(f_ort, m_ort)
                    distanz_liste.append((dist, f, m))
            
            distanz_liste.sort(key=lambda x: x[0])
            
            # Zuteilung (max 4 pro Auto)
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
                    # Wegpunkte sortieren
                    sortierte_mitfahrer = []
                    unbesucht = zugewiesene_mitfahrer.copy()
                    aktueller_ort = f_ort
                    
                    while unbesucht:
                        naechster = min(unbesucht, key=lambda x: berechne_distanz(aktueller_ort, alle_personen[x]))
                        sortierte_mitfahrer.append(naechster)
                        aktueller_ort = alle_personen[naechster]
                        unbesucht.remove(naechster)
                    
                    st.write(f"**Mitfahrer ({len(sortierte_mitfahrer)}/4 Plätze belegt):**")
                    for i, m in enumerate(sortierte_mitfahrer):
                        zusatz = " *(steigt ohne Umweg zu)*" if m in mitfahrer_ohne_umweg else ""
                        st.write(f"{i+1}. {m} ({alle_personen[m]}){zusatz}")
                    
                    url_origin = urllib.parse.quote(f"{f_ort}, Bayern, Deutschland")
                    url_dest = urllib.parse.quote(ziel)
                    
                    wegpunkte = [urllib.parse.quote(f"{alle_personen[m]}, Bayern, Deutschland") 
                                 for m in sortierte_mitfahrer if m not in mitfahrer_ohne_umweg]
                    
                    if wegpunkte:
                        url_waypoints = "|".join(wegpunkte)
                        gmaps_link = f"https://www.google.com/maps/dir/?api=1&origin={url_origin}&destination={url_dest}&waypoints={url_waypoints}"
                    else:
                        gmaps_link = f"https://www.google.com/maps/dir/?api=1&origin={url_origin}&destination={url_dest}"
                    
                    st.markdown(f"**[📍 Google Maps Route für {f} öffnen]({gmaps_link})**")
                
                st.write("---")