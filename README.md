# 🎲 BGG Guild Collection Viewer

Una aplicación web hecha en **Streamlit** para visualizar la colección de juegos de mesa de una **guild** de [BoardGameGeek](https://boardgamegeek.com), mostrando imágenes, dueños y un índice alfabético para navegar más fácilmente.

🔗 **Probar ahora:** [https://bgg-guild.streamlit.app/](https://bgg-guild.streamlit.app/)

---

## ✨ Funcionalidades

- 📥 Obtiene automáticamente la lista de miembros de una guild usando la API de BGG.
- 📚 Descarga la colección de cada miembro sin expansiones.
- 🔤 Índice alfabético para navegar fácilmente.
- 🖼️ Imágenes clicables que llevan directamente a la página del juego en BGG.

---

## 🚀 Cómo usar

1. Ingresá el **ID de la guild** de BoardGameGeek en el campo de texto.
2. Hacé clic en **Cargar colección**.
3. Usá el índice alfabético para navegar por las letras.
4. Hacé clic en cualquier imagen para ir a la ficha del juego en BGG.

---

## 🛠️ Instalación local

Si querés correrlo en tu máquina:

```bash
# 1. Clonar este repositorio
git clone https://github.com/tu-usuario/bgg-guild-app.git
cd bgg-guild-app

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la app
streamlit run guild_collection.py
