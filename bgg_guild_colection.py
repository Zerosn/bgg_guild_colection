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
# ---------------- ESTILOS CSS ----------------
st.markdown("""
<style>
.game-card-container {
    position: relative;
    display: inline-block;
    width: 100%;
    margin-bottom: 15px;
}

.game-image-wrapper {
    position: relative;
    display: inline-block;
    width: 100%;
}

.game-image-wrapper img {
    width: 100%;
    height: auto;  /* Altura automática según proporción */
    border-radius: 8px;
    display: block;
}

.hex-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 40px;
    height: 40px;
    background-color: #FF9900;
    clip-path: polygon(50% 0, 100% 20%, 100% 80%, 50% 100%, 0 80%, 0 20%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 14px;
    z-index: 2;
    text-shadow: 0 0 2px #000;
}

.game-title {
    margin-top: 8px;
    font-weight: bold;
    font-size: 14px;
    text-align: center;
    word-wrap: break-word;
    margin-bottom: 0;
}

.game-players {
    font-size: 14px;
    text-align: center;
    margin-top: 0;
}            
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCIONES ----------------
def get_rating_color(rating):
    Color_ranking = {
        "N/A": "#808080",  # Gris para sin puntuación
        "1": "#b2151f",    # Marron para puntuaciones muy bajas
        "2": "#b2151f",    # Marron para puntuaciones muy bajas
        "3": "#d71925",    # Rojo para puntuaciones bajas
        "4": "#d71925",    # Rojo claro para puntuaciones bajas
        "5": "#5369a2",    # azul para puntuaciones medias bajas
        "6": "#5369a2",    # azul para puntuaciones medias bajas
        "7": "#1978b3",    # Celeste puntuaciones medias
        "8": "#1d804c",    # Verde claro para puntuaciones altas
        "9": "#186b40",    # Verde para puntuaciones muy altas
        "10": "#186b40",   # Verde claro para puntuaciones muy altas
    }
    if rating is None or rating == "N/A":
        return Color_ranking["N/A"]
    try:
        rating_index = f"{rating:.0f}"
        return Color_ranking.get(rating_index, "#808080")  # Gris por defecto
    except:
        return "#808080"
    
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
    url = f"https://boardgamegeek.com/xmlapi2/collection?username={username}&own=1&excludesubtype=boardgameexpansion&stats=1"
    root = fetch_xml(url)
    if root is None:
        return []
    games = []
    for item in root.findall("item"):
        games.append({
            "id": item.attrib["objectid"],
            "name": item.find("name").text,
            "image": item.find("image").text if item.find("image") is not None else None,
            "owner": username,
            "score": item.find('stats').find('rating').find("average").attrib.get("value", "N/A"),
            "minplayers":item.find('stats').attrib.get("minplayers", "N/A"),
            "maxplayers":item.find('stats').attrib.get("maxplayers", "N/A")
        })
    return games

# ---------------- INTERFAZ ----------------
st.title("Visor de Colecciónes de Guild")
guild_id = st.text_input("Ingrese el ID de la Guild de la bgg:", "4523")

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

            # Eliminar duplicados por ID
            unique_games = {g["id"]: g for g in all_games}.values()
            url = f"https://boardgamegeek.com/xmlapi2/guild?id={guild_id}"
            root = fetch_xml(url)
            guild_name = root.attrib.get("name", "Nombre no disponible")
            st.title(f"Guid: {guild_name}")
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
                        rating = game.get('score', None)
                        if rating is not None and rating != "N/A":
                            rating = float(rating)
                            rating_display = f"{rating:.1f}"
                        else:
                            rating = None
                            rating_display = "N/A"
                        

                        color = get_rating_color(rating)  # Usa tu función existente

                        html = f"""
                                <div class="game-card-container">
                                    <div class="game-image-wrapper">
                                        <a href='{game_url}' target='_blank'>
                                            <img src='{game["image"]}' 
                                                onerror="this.src='https://via.placeholder.com/300x400?text=Sin+imagen'">
                                        </a>
                                        <div class="hex-badge" style="background-color: {color};">
                                            {rating_display}
                                        </div>
                                    </div>
                                    <p class="game-title">{game['name']}</p>
                                    <p class="game-players">({game['minplayers']} - {game['maxplayers']} jugadores)</p>
                                </div>
                                """

                        st.markdown(html, unsafe_allow_html=True)
                    col_idx = (col_idx + 1) % 5
