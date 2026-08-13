import streamlit as st

st.title("🚗 Therapie-Fahrplan")
st.write("Hier verteilen wir unsere Fahrer und berechnen die effizientesten Routen!")

# Das Gedächtnis der App einrichten: Eine Liste für alle Gäste
if 'gaeste' not in st.session_state:
    st.session_state.gaeste = {}

# Eure feste Gruppe
feste_gruppe = {
    "Jona": "Wiesenthau",
    "Till": "Wannbach",
    "Felix": "Unterzaunsbach",
    "Valentin": "Ebermannstadt",
    "Tim": "Dürrbrunn",
    "Jonas": "Kleingesee",
    "Moritz Taglauer": "Kandorf",
    "Moritz Burkhard": "Gasseldorf",
    "Andreas": "Türkenstein"
}

st.header("👥 Einmalige Gäste")
st.write("Fahren heute noch Leute spontan mit?")

# Eingabefelder für neue Gäste
col1, col2 = st.columns(2)
neuer_gast_name = col1.text_input("Name des Gastes:")
neuer_gast_ort = col2.text_input("Wohnort (z.B. Forchheim):")

# Ein Button, um den Gast zur Liste hinzuzufügen
if st.button("Gast hinzufügen"):
    if neuer_gast_name and neuer_gast_ort:
        st.session_state.gaeste[neuer_gast_name] = neuer_gast_ort
        st.success(f"{neuer_gast_name} aus {neuer_gast_ort} wurde hinzugefügt!")
    else:
        st.warning("Bitte Name und Wohnort eingeben.")

# Anzeigen der bisher hinzugefügten Gäste
if st.session_state.gaeste:
    st.write("Bisher hinzugefügte Gäste:")
    for gast, ort in st.session_state.gaeste.items():
        st.write(f"- {gast} ({ort})")

# Eine gemeinsame Liste aus der festen Gruppe und den Gästen erstellen
alle_personen = {**feste_gruppe, **st.session_state.gaeste}
alle_namen = list(alle_personen.keys())

st.divider()

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

if st.button("Route berechnen"):
    if not fahrer:
        st.error("Bitte wähle mindestens einen Fahrer aus!")
    elif not mitfahrer:
        st.error("Bitte wähle mindestens einen Mitfahrer aus!")
    else:
        st.success(f"App ist bereit! {len(fahrer)} Auto(s) holen {len(mitfahrer)} Person(en) ab.")
        
        st.write("Gewählte Fahrer:", ", ".join(fahrer))
        st.write("Gewählte Mitfahrer:", ", ".join(mitfahrer))