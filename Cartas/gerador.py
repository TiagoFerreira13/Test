import streamlit as st
import json
import os
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Constants for file paths
FONT_URL = "https://github.com/TiagoFerreira13/Test/raw/refs/heads/main/Cartas/Rajdhani/Rajdhani-Regular.ttf"
FONT_PATH = "Rajdhani-Regular.ttf"
ATTACK_TEMPLATE_URL = "https://github.com/TiagoFerreira13/Test/raw/main/Cartas/templates/attackcard.png"
DEFENSE_TEMPLATE_URL = "https://github.com/TiagoFerreira13/Test/raw/main/Cartas/templates/defensecard.png"
ATTACK_TEMPLATE_PATH = "attackcard.png"
DEFENSE_TEMPLATE_PATH = "defensecard.png"
OUTPUT_DIR = "output"

# Ensure the font and templates are downloaded
def download_file(url, filename):
    if not os.path.exists(filename):
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
        else:
            print(f"Failed to download {filename}")

# Download required assets
download_file(FONT_URL, FONT_PATH)
download_file(ATTACK_TEMPLATE_URL, ATTACK_TEMPLATE_PATH)
download_file(DEFENSE_TEMPLATE_URL, DEFENSE_TEMPLATE_PATH)

# Load font safely
try:
    title_font = ImageFont.truetype(FONT_PATH, 48)
    category_font = ImageFont.truetype(FONT_PATH, 28)
    desc_font = ImageFont.truetype(FONT_PATH, 28)
except OSError:
    st.error("Font failed to load. Using default font.")
    title_font = ImageFont.load_default()
    category_font = ImageFont.load_default()
    desc_font = ImageFont.load_default()

# Streamlit app
def main():
    st.title("Criador de Cartas de Cibersegurança")

    # Session state for storing cards
    if "cards_attack" not in st.session_state:
        st.session_state["cards_attack"] = []
    if "cards_defense" not in st.session_state:
        st.session_state["cards_defense"] = []

    # Card Input Fields
    deck = st.text_input("Deck")
    title = st.text_input("Título")
    card_type = st.selectbox("Tipo", ["Ataque", "Defesa"])
    description = st.text_area("Descrição")
    quote = st.text_area("Quote")

    # Image Upload
    image = st.file_uploader("Upload de Imagem", type=["png", "jpg", "jpeg"])

    # Ensure 'uploads' directory exists before saving the image
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)  

    image_path = None  # Default to None if no image is uploaded
    if image:
        image_path = os.path.join(upload_dir, image.name)
        with open(image_path, "wb") as f:
            f.write(image.getbuffer())

    # Add card
    if st.button("Adicionar Carta"):
        if not title or not description:
            st.error("O título e descrição são obrigatórios!")
        else:
            card = {
                "deck": deck.strip(),
                "title": title.strip(),
                "state": "draft/ready",
                "image": image_path,
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
                "attack": {"base_image": ATTACK_TEMPLATE_PATH, "cards": st.session_state["cards_attack"]},
                "defense": {"base_image": DEFENSE_TEMPLATE_PATH, "cards": st.session_state["cards_defense"]}
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
        with open("cartas.json", "r", encoding="utf-8") as f:
            base = json.load(f)

        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

    # Function to draw text
    def draw_text(draw, text, font, box, align="left", fill=(255, 255, 255)):
        x, y, w, h = box
        lines = textwrap.wrap(text, width=30 if align == "center" else 40)

        bbox = draw.textbbox((0, 0), "A", font=font)  # Measure text height correctly
        line_height = (bbox[3] - bbox[1]) + 6
        current_y = y
    
        for line in lines:
            line_bbox = draw.textbbox((0, 0), line, font=font)
            line_width = line_bbox[2] - line_bbox[0]
    
            if align == "center":
                line_x = x + (w - line_width) // 2
            else:
                line_x = x
    
            draw.text((line_x, current_y), line, font=font, fill=fill)
            current_y += line_height

        # Process each card
        for flavor in ["attack", "defense"]:
            template_path = base["flavors"][flavor]["base_image"]
            category_label = "Ataque" if flavor == "attack" else "Defesa"
            cards = base["flavors"][flavor]["cards"]

            for card in cards:
                template = Image.open(template_path).convert("RGBA")
                draw = ImageDraw.Draw(template)

                draw_text(draw, card["title"], title_font, base["layout"]["title_box"], align="center")
                draw_text(draw, category_label, category_font, base["layout"]["category_box"], align="left")
                draw_text(draw, card["description"], desc_font, base["layout"]["desc_box"], align="justified")
                if card["quote"]:
                    draw_text(draw, card["quote"], desc_font, base["layout"]["quote_box"], align="justified")

                # Paste image if available
                if card["image"] and os.path.exists(card["image"]):
                    x, y, w, h = base["layout"]["image_box"]
                    card_image = Image.open(card["image"]).convert("RGBA")
                    card_image = ImageOps.fit(card_image, (int(w), int(h)), Image.Resampling.LANCZOS)
                    template.paste(card_image, (x, y), card_image)

                filename = f"{card['deck'].replace(' ', '_')}_{card['title'].replace(' ', '_')}.png"
                template.save(os.path.join(OUTPUT_DIR, filename))
                st.success(f"Carta '{card['title']}' gerada!")

if __name__ == "__main__":
    main()
