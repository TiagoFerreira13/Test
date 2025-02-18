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
missing_files = [f for f in TEMPLATE_URLS.keys() if not os.path.exists(os.path.join(TEMPLATE_FOLDER, f))]
if missing_files:
    st.error(f"Some template files are missing: {', '.join(missing_files)}")

def generate_cards(json_data):
    font_path = os.path.join(TEMPLATE_FOLDER, "Rajdhani-Regular.ttf")

    # Ensure font exists before loading
    if not os.path.exists(font_path):
        st.error("Font file is missing! Cannot generate cards.")
        return
    
    try:
        title_font = ImageFont.truetype(font_path, 48)
        category_font = ImageFont.truetype(font_path, 28)
        desc_font = ImageFont.truetype(font_path, 28)
    except OSError as e:
        st.error(f"Error loading font: {e}")
        return

    for flavor in ["attack", "defense"]:
        template_path = json_data["flavors"][flavor]["base_image"]
        if not os.path.exists(template_path):
            st.error(f"Template image for {flavor} is missing!")
            return
        
        cards = json_data["flavors"][flavor]["cards"]
        for card in cards:
            template = Image.open(template_path).convert("RGBA")
            draw = ImageDraw.Draw(template)
            
            draw.text((175, 83), card["title"], font=title_font, fill="white", align="center")
            draw.text((115, 444), flavor.capitalize(), font=category_font, fill="white")
            draw.text((115, 495), card["description"], font=desc_font, fill="white")

            if card.get("quote"):
                draw.text((115, 685), card["quote"], font=desc_font, fill="white")

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
