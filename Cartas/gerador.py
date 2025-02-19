import json
import os
import shutil
import textwrap
from io import BytesIO

import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Constants
FONT_URL = "https://github.com/TiagoFerreira13/Test/raw/refs/heads/main/Cartas/Rajdhani/Rajdhani-Regular.ttf"
FONT_PATH = "Rajdhani-Regular.ttf"
ATTACK_TEMPLATE_URL = "https://github.com/TiagoFerreira13/Test/raw/main/Cartas/templates/attackcard.png"
DEFENSE_TEMPLATE_URL = "https://github.com/TiagoFerreira13/Test/raw/main/Cartas/templates/defensecard.png"
OUTPUT_DIR = "output"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Download assets if missing
def download_file(url, filename):
    if not os.path.exists(filename):
        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.RequestException as e:
            st.error(f"Error downloading {filename}: {e}")

download_file(FONT_URL, FONT_PATH)
download_file(ATTACK_TEMPLATE_URL, "attackcard.png")
download_file(DEFENSE_TEMPLATE_URL, "defensecard.png")

# Load font safely
def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except IOError:
        st.error(f"Failed to load font: {path}")
        return ImageFont.load_default()

title_font = load_font(FONT_PATH, 48)
category_font = load_font(FONT_PATH, 28)
desc_font = load_font(FONT_PATH, 28)

def main():
    st.title("Criador de Cartas de Cibersegurança")

    # Session state for storing cards
    if "cards_attack" not in st.session_state:
        st.session_state["cards_attack"] = []
    if "cards_defense" not in st.session_state:
        st.session_state["cards_defense"] = []

    # Input fields
    deck = st.text_input("Deck")
    title = st.text_input("Título")
    card_type = st.selectbox("Tipo", ["Ataque", "Defesa"])
    description = st.text_area("Descrição")
    quote = st.text_area("Quote")
    state = st.selectbox("Estado", ["draft", "ready"])

    # Image upload (keeps in memory instead of writing to disk)
    uploaded_image = st.file_uploader("Upload de Imagem", type=["png", "jpg", "jpeg"])
    image_bytes = None
    if uploaded_image:
        image_bytes = BytesIO(uploaded_image.getbuffer())

    # Add card
    if st.button("Adicionar Carta"):
        if not title or not description:
            st.error("Título e descrição são obrigatórios!")
        else:
            card = {
                "deck": deck.strip(),
                "title": title.strip(),
                "state": state,
                "image": image_bytes,
                "description": description.strip(),
                "quote": quote.strip()
            }

            if card_type == "Ataque":
                st.session_state["cards_attack"].append(card)
            else:
                st.session_state["cards_defense"].append(card)

            st.success(f"Carta '{title}' adicionada!")

    # Display Cards
    st.subheader("Cartas de Defesa")
    for card in st.session_state["cards_defense"]:
        st.text(f"- {card['title']}")

    st.subheader("Cartas de Ataque")
    for card in st.session_state["cards_attack"]:
        st.text(f"- {card['title']}")

    # Generate JSON
    if st.button("Gerar JSON"):
        json_data = {
            "flavors": {
                "attack": {"base_image": "attackcard.png", "cards": st.session_state["cards_attack"]},
                "defense": {"base_image": "defensecard.png", "cards": st.session_state["cards_defense"]}
            },
            "font": {"path": FONT_PATH, "title_size": 48, "category_size": 28, "desc_size": 28},
            "layout": {
                "title_box": [175, 83, 400, 60],
                "image_box": [107, 151, 530, 282.5],
                "category_box": [115, 444, 300, 40],
                "desc_box": [115, 495, 500, 180],
                "quote_box": [115, 685, 500, 100]
            },
            "output_dir": OUTPUT_DIR
        }
        
        json_filename = "cartas.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        
        st.success("JSON gerado com sucesso!")
        st.download_button("Baixar JSON", json.dumps(json_data, ensure_ascii=False, indent=4), json_filename, "application/json")

    # Generate Cards
    if st.button("Gerar Cartas"):
        if not st.session_state["cards_attack"] and not st.session_state["cards_defense"]:
            st.error("Erro: Nenhuma carta adicionada.")
            return

        with open("cartas.json", "r", encoding="utf-8") as f:
            base = json.load(f)

        # Clear previous images
        shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR)

        for flavor in ["attack", "defense"]:
            template_path = base["flavors"][flavor]["base_image"]
            category_label = "Ataque" if flavor == "attack" else "Defesa"

            for card in base["flavors"][flavor]["cards"]:
                template = Image.open(template_path).convert("RGBA")
                draw = ImageDraw.Draw(template)

                draw_text(draw, card["title"], title_font, base["layout"]["title_box"])
                draw_text(draw, category_label, category_font, base["layout"]["category_box"])
                draw_text(draw, card["description"], desc_font, base["layout"]["desc_box"])
                draw_text(draw, card["quote"], desc_font, base["layout"]["quote_box"])

                if card["image"]:
                    x, y, w, h = base["layout"]["image_box"]
                    card_image = Image.open(card["image"]).convert("RGBA")
                    card_image = ImageOps.fit(card_image, (int(w), int(h)), Image.LANCZOS)
                    template.paste(card_image, (x, y), card_image)

                output_filename = f"{card['deck'].replace(' ', '_')}_{card['title'].replace(' ', '_')}.png"
                template.save(os.path.join(OUTPUT_DIR, output_filename))
                st.success(f"Carta '{card['title']}' gerada!")

        zip_filename = shutil.make_archive("cartas", "zip", OUTPUT_DIR)
        with open(zip_filename, "rb") as zip_file:
            st.download_button("Baixar Todas as Cartas", zip_file, file_name="cartas.zip", mime="application/zip")

# Function to draw text
def draw_text(draw, text, font, box, fill=(255, 255, 255), width=40):
    x, y, w, h = box
    lines = textwrap.wrap(text, width=width)
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=fill)
        current_y += font.size + 6  # Spacing between lines

main()
