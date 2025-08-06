import requests
import xml.etree.ElementTree as ET
import streamlit as st
import time
import string
from collections import Counter

# ---------------- CONFIG STREAMLIT ----------------
st.set_page_config(
    page_title="Colección de Guild BGG",
    page_icon="🎲",
    layout="wide"
)

# ---------------- FUNCIONES ----------------
def fetch_xml(url, max_retries=5, wait=2):
    """Descarga XML desde una URL con reintentos."""
    for _ in range(max_retries):
        r = requests.get(url)
        if r.status_code == 200 and r.content.strip():
            try:
                return ET.fromstring(r.content)
            except ET.ParseError:
                pass
        time.sleep(wait)
    return None

@st.cache_data(ttl=3600)
def get_guild_members(guild_id):
    """Obtiene lista completa de miembros con paginación."""
    members = []
    page = 1
    while True:
        url = f"https://boardgamegeek.com/xmlapi2/guild?id={guild_id}&members=1&page={page}"
        root = fetch_xml(url)
        if root is None:
            break
        page_members = [m.attrib["name"] for m in root.findall(".//member")]
        if not page_members:
            break
        members.extend(page_members)
        page += 1
    return members

@st.cache_data(ttl=3600)
def get_collection(username):
    """Obtiene la colección de un usuario."""
    url = f"https://boardgamegeek.com/xmlapi2/collection?username={username}&own=1"
    root = fetch_xml(url)
    if root is None:
        return []
    games = []
    for item in root.findall("item"):
        games.append({
            "id": item.attrib["objectid"],
            "name": item.find("name").text,
            "image": item.find("image").text if item.find("thumbnail") is not None else None,
            "owner": username
        })
    return games

# ---------------- INTERFAZ ----------------
st.title("🎲 Colección de la Guild en BoardGameGeek")
guild_id = st.text_input("Ingrese el ID de la Guild:", "4523")

if st.button("Cargar colección"):
    with st.spinner("Descargando datos..."):
        members = get_guild_members(guild_id)
        if not members:
            st.error("No se encontraron miembros o hubo un error en la conexión.")
        else:
            all_games = []
            for user in members:
                games = get_collection(user)
                all_games.extend(games)
            # Nombre Guild
            url = f"https://boardgamegeek.com/xmlapi2/guild?id={guild_id}"
            root = fetch_xml(url)
            guild_name = root.attrib.get("name", "Nombre no disponible")
            st.title(f"Guid: {guild_name}")
            # Eliminar duplicados por ID
            unique_games = {g["id"]: g for g in all_games}.values()

            # ---- AGRUPAR POR LETRA ----
            games_sorted = sorted(unique_games, key=lambda x: x["name"].lower())
            games_by_letter = {letter: [] for letter in string.ascii_uppercase}
            games_by_letter["#"] = []  # Otros caracteres

            for game in games_sorted:
                first_char = game["name"][0].upper()
                if first_char in games_by_letter:
                    games_by_letter[first_char].append(game)
                else:
                    games_by_letter["#"].append(game)

            # ---- BARRA DE ÍNDICE ----
            st.sidebar.title("📇 Índice")
            for letter in games_by_letter.keys():
                st.sidebar.markdown(f"[{letter}](#{letter.lower()})", unsafe_allow_html=True)

            # ---- MOSTRAR POR LETRA ----
            for letter, games_list in games_by_letter.items():
                if not games_list:
                    continue
                st.markdown(f"<h2 id='{letter.lower()}'>{letter}</h2>", unsafe_allow_html=True)
                cols = st.columns(5)
                col_idx = 0
                for game in games_list:
                    with cols[col_idx]:
                        game_url = f"https://boardgamegeek.com/boardgame/{game['id']}"
                        st.markdown(
                            f"<a href='{game_url}' target='_blank'><img src='{game['image']}' width='100%'></a>",
                            unsafe_allow_html=True
                        )
                        st.caption(f"{game['name']} ({game['owner']})")
                    col_idx = (col_idx + 1) % 5

