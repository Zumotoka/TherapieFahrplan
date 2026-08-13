import streamlit as st

st.title("🚗 Therapie-Fahrplan")
st.write("Hier verteilen wir unsere Fahrer und berechnen die effizientesten Routen!")

# Eure komplette Gruppe mit den genauen Wohnorten
freunde_orte = {
    "Jona": "Wiesenthau",
    "Till": "Wannbach",
    "Felix": "Unterzaunsbach",
    "Valentin": "Ebermannstadt",
    "Tim": "Dürrbrunn",
    "Jonas": "Plein-Gesee",
    "Moritz Taglauer": "Kandorf",
    "Moritz Burkhard": "Kasseldorf",
    "Andreas": "Türkenstein"
}

st.header("👥 Einmaliger Gast")
st.write("Fährt heute noch jemand spontan mit?")

# st.columns(2) erstellt zwei Spalten, damit die Felder schön nebeneinander stehen
col1, col2 = st.columns(2)
gast_name = col1.text_input("Name des Gastes:")
gast_ort = col2.text_input("Wohnort (z.B. Forchheim):")

# Wenn in beide Felder etwas eingetippt wurde, wird der Gast zur Liste hinzugefügt
if gast_name and gast_ort:
    freunde_orte[gast_name] = gast_ort

# Erst jetzt holen wir uns die Liste aller Namen (inklusive des möglichen Gastes)
freunde = list(freunde_orte.keys())

st.header("1. Wer fährt heute?")
fahrer = st.multiselect(
    "Fahrer auswählen:", 
    freunde, 
    format_func=lambda x: f"{x} ({freunde_orte[x]})"
)

st.header("2. Wer muss abgeholt werden?")
# Logik: Wer fährt, verschwindet automatisch aus der Mitfahrer-Liste
mitfahrer_optionen = [person for person in freunde if person not in fahrer]
mitfahrer = st.multiselect(
    "Mitfahrer auswählen:", 
    mitfahrer_optionen,
    format_func=lambda x: f"{x} ({freunde_orte[x]})"
)

st.divider() 

if st.button("Route berechnen"):
    if not fahrer:
        st.error("Bitte wähle mindestens einen Fahrer aus!")
    elif not mitfahrer:
        st.error("Bitte wähle mindestens einen Mitfahrer aus!")
    else:
        st.success(f"App ist bereit! {len(fahrer)} Auto(s) holen {len(mitfahrer)} Person(en) ab.")
        st.info("Im nächsten Schritt bereiten wir die Daten für die echte Karte vor.")