import streamlit as st
import json
import os
import urllib.request
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Define template folder
TEMPLATE_FOLDER = "templates"
os.makedirs(TEMPLATE_FOLDER, exist_ok=True)

# URLs to GitHub RAW files (Update with your actual repo)
TEMPLATE_URLS = {
    "attackcard.png": "https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO/main/templates/attackcard.png",
    "defensecard.png": "https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO/main/templates/defensecard.png",
    "Rajdhani-Regular.ttf": "https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO/main/fonts/Rajdhani-Regular.ttf"
}

# Ensure templates exist
for filename, url in TEMPLATE_URLS.items():
    filepath = os.path.join(TEMPLATE_FOLDER, filename)
    if not os.path.exists(filepath):
        try:
            st.write(f"Downloading {filename} from GitHub...")
            urllib.request.urlretrieve(url, filepath)
        except Exception as e:
            st.error(f"Failed to download {filename}: {e}")

# Confirm files exist
if not all(os.path.exists(os.path.join(TEMPLATE_FOLDER, f)) for f in TEMPLATE_URLS.keys()):
    st.error("Some template images are missing! Please check the templates folder.")

def draw_text(draw, text, font, box, align="left", fill=(255,255,255)):
    x, y, w, h = box
    wrap_width = 30 if align == "center" else 40
    lines = textwrap.wrap(text, width=wrap_width)
    bbox_ref = draw.textbbox((0, 0), "A", font=font)
    line_height = (bbox_ref[3] - bbox_ref[1]) + 6
    current_y = y
    
    for i, line in enumerate(lines):
        if align == "justified" and i < len(lines) - 1:
            words = line.split()
            total_words_width = sum(draw.textbbox((0,0), word, font=font)[2] for word in words)
            total_space = w - total_words_width
            space_count = len(words) - 1
            space_width = total_space // space_count if space_count > 0 else 0
            current_x = x
            for j, word in enumerate(words):
                draw.text((current_x, current_y), word, font=font, fill=fill)
                wbbox = draw.textbbox((0,0), word, font=font)
                word_width = wbbox[2] - wbbox[0]
                current_x += word_width + space_width
        else:
            line_bbox = draw.textbbox((0,0), line, font=font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = x + (w - line_width) // 2 if align == "center" else x
            draw.text((line_x, current_y), line, font=font, fill=fill)
        current_y += line_height

def generate_cards(json_data):
    font_path = os.path.join(TEMPLATE_FOLDER, "Rajdhani-Regular.ttf")
    title_font = ImageFont.truetype(font_path, 48)
    category_font = ImageFont.truetype(font_path, 28)
    desc_font = ImageFont.truetype(font_path, 28)
    
    for flavor in ["attack", "defense"]:
        template_path = json_data["flavors"][flavor]["base_image"]
        cards = json_data["flavors"][flavor]["cards"]
        for card in cards:
            template = Image.open(template_path).convert("RGBA")
            draw = ImageDraw.Draw(template)
            
            draw_text(draw, card["title"], title_font, (175, 83, 400, 60), align="center")
            draw_text(draw, flavor.capitalize(), category_font, (115, 444, 300, 40), align="left")
            draw_text(draw, card["description"], desc_font, (115, 495, 500, 180), align="justified")
            if card.get("quote"):
                draw_text(draw, card["quote"], desc_font, (115, 685, 500, 100), align="justified")
            
            filename = f"{card['deck'].replace(' ', '_')}_{card['title'].replace(' ', '_')}.png"
            template.save(filename)
            st.download_button(f"Baixar {filename}", open(filename, "rb"), filename, "image/png")

def main():
    st.title("Criador de Cartas de Cibersegurança")
    
    if "cards_attack" not in st.session_state:
        st.session_state["cards_attack"] = []
    if "cards_defense" not in st.session_state:
        st.session_state["cards_defense"] = []
    if "deck" not in st.session_state:
        st.session_state["deck"] = ""
    
    deck = st.text_input("Deck", value=st.session_state["deck"])
    title = st.text_input("Título")
    card_type = st.selectbox("Tipo", ["Ataque", "Defesa"], index=None, disabled=False)
    description = st.text_area("Descrição")
    quote = st.text_area("Quote")
    image = st.file_uploader("Upload de Imagem", type=["png", "jpg", "jpeg"])
    
    if st.button("Adicionar Carta"):
        if not title or not description or card_type is None:
            st.error("O título, tipo e descrição são obrigatórios!")
        else:
            card = {
                "deck": deck.strip(),
                "title": title.strip(),
                "state": "draft/ready",
                "image": image.name if image else "images/",
                "description": description.strip(),
                "quote": quote.strip()
            }
            
            if card_type == "Ataque":
                st.session_state["cards_attack"].append(card)
            else:
                st.session_state["cards_defense"].append(card)
            
            st.success(f"Carta '{title}' adicionada com sucesso!")
            st.session_state["deck"] = deck.strip()
    
    st.subheader("Cartas de Ataque")
    for card in st.session_state["cards_attack"]:
        st.text(f"- {card['title']}")
    
    st.subheader("Cartas de Defesa")
    for card in st.session_state["cards_defense"]:
        st.text(f"- {card['title']}")
    
    if st.button("Gerar JSON e Cartas"):
        json_data = {
            "flavors": {
                "attack": {"base_image": os.path.join(TEMPLATE_FOLDER, "attackcard.png"), "cards": st.session_state["cards_attack"]},
                "defense": {"base_image": os.path.join(TEMPLATE_FOLDER, "defensecard.png"), "cards": st.session_state["cards_defense"]}
            }
        }
        json_filename = "cartas.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        st.success("JSON e cartas geradas com sucesso!")
        st.download_button("Baixar JSON", json.dumps(json_data, ensure_ascii=False, indent=4), json_filename, "application/json")
        generate_cards(json_data)

if __name__ == "__main__":
    main()
