import streamlit as st

st.title("🚗 Therapie-Fahrplan")
st.write("Hier verteilen wir unsere Fahrer und berechnen die effizientesten Routen!")

# Eure komplette Gruppe
freunde = [
    "Jona (Wiesentau)", 
    "Till (Wannbach)", 
    "Felix (Unterzaunsbach)", 
    "Valentin", 
    "Tim", 
    "Jonas", 
    "Moritz Taglauer", 
    "Moritz Burkhard", 
    "Andreas"
]

st.header("1. Wer fährt heute?")
# multiselect erlaubt es, auch mehrere Fahrer (z.B. für zwei Autos) auszuwählen
fahrer = st.multiselect("Fahrer auswählen:", freunde)

st.header("2. Wer muss abgeholt werden?")
# Logik: Wer fährt, verschwindet automatisch aus der Mitfahrer-Liste!
mitfahrer_optionen = [person for person in freunde if person not in fahrer]
mitfahrer = st.multiselect("Mitfahrer auswählen:", mitfahrer_optionen)

st.divider() # Zieht einen schönen Trennstrich

if st.button("Route berechnen"):
    if not fahrer:
        st.error("Bitte wähle mindestens einen Fahrer aus!")
    elif not mitfahrer:
        st.error("Bitte wähle mindestens einen Mitfahrer aus!")
    else:
        st.success(f"App ist bereit! {len(fahrer)} Auto(s) holen {len(mitfahrer)} Person(en) ab.")
        st.info("Im nächsten Schritt bauen wir hier die echte Routenberechnung ein.")