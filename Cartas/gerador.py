import streamlit as st
import json
import os
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Create necessary directories
os.makedirs("user_images", exist_ok=True)
os.makedirs("output", exist_ok=True)

# URLs for templates and font
ASSETS = {
    "attack_card": "https://raw.githubusercontent.com/TiagoFerreira13/Test/main/Cartas/templates/attackcard.png",
    "defense_card": "https://raw.githubusercontent.com/TiagoFerreira13/Test/main/Cartas/templates/defensecard.png",
    "font": "https://github.com/TiagoFerreira13/Test/raw/main/Cartas/Rajdhani/Rajdhani-Regular.ttf"
}

FONT_PATH = os.path.abspath("Rajdhani-Regular.ttf")  # Absolute path for reliability

# Download assets if they don't exist
def download_file(url, filename):
    if not os.path.exists(filename):
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
        else:
            st.error(f"Failed to download {filename}")

# Download assets
for key, url in ASSETS.items():
    download_file(url, f"{key}.png" if "card" in key else FONT_PATH)

# 🔍 Verify font integrity
try:
    test_font = ImageFont.truetype(FONT_PATH, 24)
except Exception as e:
    st.error(f"Font failed to load: {e}")
    st.stop()  # Stop execution if the font is broken

# ✅ Font is confirmed working at this point

def main():
    st.title("Criador de Cartas de Cibersegurança")

    if "cards_attack" not in st.session_state:
        st.session_state["cards_attack"] = []
    if "cards_defense" not in st.session_state:
        st.session_state["cards_defense"] = []

    title = st.text_input("Título")
    card_type = st.selectbox("Tipo", ["Ataque", "Defesa"], index=None)
    description = st.text_area("Descrição")
    quote = st.text_area("Quote")
    image = st.file_uploader("Upload de Imagem", type=["png", "jpg", "jpeg"])

    if st.button("Adicionar Carta"):
        if not title or not description or card_type is None:
            st.error("O título, tipo e descrição são obrigatórios!")
        else:
            image_path = None
            if image:
                image_path = os.path.join("user_images", image.name)
                with open(image_path, "wb") as f:
                    f.write(image.getbuffer())

            card = {
                "title": title.strip(),
                "state": "draft/ready",
                "image": image_path if image else None,
                "description": description.strip(),
                "quote": quote.strip()
            }

            if card_type == "Ataque":
                st.session_state["cards_attack"].append(card)
            else:
                st.session_state["cards_defense"].append(card)

            st.success(f"Carta '{title}' adicionada com sucesso!")

    # Generate Cards
    if st.button("Gerar Cartas"):
        title_font = ImageFont.truetype(FONT_PATH, 48)
        category_font = ImageFont.truetype(FONT_PATH, 28)
        desc_font = ImageFont.truetype(FONT_PATH, 28)

        def draw_text(draw, text, font, box):
            x, y, w, h = box
            lines = textwrap.wrap(text, width=40)
            line_height = font.getsize("A")[1] + 6
            current_y = y

            for line in lines:
                line_width = font.getsize(line)[0]
                draw.text((x + (w - line_width) // 2, current_y), line, font=font, fill=(255,255,255))
                current_y += line_height

        for card in st.session_state["cards_attack"] + st.session_state["cards_defense"]:
            template_path = "attack_card.png" if card in st.session_state["cards_attack"] else "defense_card.png"
            template = Image.open(template_path).convert("RGBA")
            draw = ImageDraw.Draw(template)

            draw_text(draw, card["title"], title_font, [175, 83, 400, 60])
            draw_text(draw, "Ataque" if card in st.session_state["cards_attack"] else "Defesa", category_font, [115, 444, 300, 40])
            draw_text(draw, card["description"], desc_font, [115, 495, 500, 180])

            filename = f
