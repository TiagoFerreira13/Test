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
    "font": "https://raw.githubusercontent.com/TiagoFerreira13/Test/raw/refs/heads/main/Cartas/Rajdhani/Rajdhani-Regular.ttf"
}

# Download assets if they don't exist
def download_file(url, filename):
    if not os.path.exists(filename):
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
        else:
            st.error(f"Failed to download {filename}")

# Download and save
for key, url in ASSETS.items():
    download_file(url, f"{key}.png" if "card" in key else "Rajdhani-Regular.ttf")

# Load font path
FONT_PATH = "Rajdhani-Regular.ttf"

def main():
    st.title("Criador de Cartas de Cibersegurança")

    # Initialize session state
    if "cards_attack" not in st.session_state:
        st.session_state["cards_attack"] = []
    if "cards_defense" not in st.session_state:
        st.session_state["cards_defense"] = []
    if "deck" not in st.session_state:
        st.session_state["deck"] = ""

    # Input Fields
    deck = st.text_input("Deck", value=st.session_state["deck"])
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
                "deck": deck.strip(),
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
            st.session_state["deck"] = deck.strip()  # Preserve deck value

    # Display stored cards
    st.subheader("Cartas de Ataque")
    for card in st.session_state["cards_attack"]:
        st.text(f"- {card['title']}")

    st.subheader("Cartas de Defesa")
    for card in st.session_state["cards_defense"]:
        st.text(f"- {card['title']}")

    # Generate JSON
    if st.button("Gerar JSON"):
        json_data = {
            "flavors": {
                "attack": {"base_image": "attack_card.png", "cards": st.session_state["cards_attack"]},
                "defense": {"base_image": "defense_card.png", "cards": st.session_state["cards_defense"]}
            },
            "font": {
                "path": FONT_PATH,
                "title_size": 48,
                "category_size": 28,
                "desc_size": 28
            },
            "layout": {
                "title_box": [175, 83, 400, 60],
                "image_box": [107, 151, 530, 282.5],
                "category_box": [115, 444, 300, 40],
                "desc_box": [115, 495, 500, 180],
                "quote_box": [115, 685, 500, 100]
            },
            "output_dir": "output"
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

        font_conf = base["font"]
        layout = base["layout"]
        output_dir = base["output_dir"]

        # Load fonts
        title_font = ImageFont.truetype(font_conf["path"], font_conf["title_size"])
        category_font = ImageFont.truetype(font_conf["path"], font_conf["category_size"])
        desc_font = ImageFont.truetype(font_conf["path"], font_conf["desc_size"])

        def draw_text(draw, text, font, box, align="left", fill=(255,255,255)):
            x, y, w, h = box
            lines = textwrap.wrap(text, width=40)
            line_height = font.getsize("A")[1] + 6
            current_y = y

            for line in lines:
                line_width = font.getsize(line)[0]
                line_x = x + (w - line_width) // 2 if align == "center" else x
                draw.text((line_x, current_y), line, font=font, fill=fill)
                current_y += line_height

        # Generate cards
        for flavor in ["attack", "defense"]:
            template_path = base["flavors"][flavor]["base_image"]
            category_label = "Ataque" if flavor == "attack" else "Defesa"
            cards = base["flavors"][flavor]["cards"]

            for card in cards:
                template = Image.open(template_path).convert("RGBA")
                draw = ImageDraw.Draw(template)

                draw_text(draw, card["title"], title_font, layout["title_box"], align="center")

                if card.get("image") and os.path.exists(card["image"]):
                    x_img, y_img, box_w, box_h = layout["image_box"]
                    card_image = Image.open(card["image"]).convert("RGBA")
                    card_image = ImageOps.fit(card_image, (int(box_w), int(box_h)), Image.Resampling.LANCZOS)
                    template.paste(card_image, (x_img, y_img), card_image)

                draw_text(draw, category_label, category_font, layout["category_box"])
                draw_text(draw, card["description"], desc_font, layout["desc_box"])
                
                if card.get("quote"):
                    draw_text(draw, card["quote"], desc_font, layout["quote_box"])

                deck = card["deck"].strip()
                filename = f"{deck.replace(' ', '_')}_{card['title'].replace(' ', '_')}.png"
                template.save(os.path.join(output_dir, filename))
                st.success(f"Carta '{card['title']}' gerada!")

if __name__ == "__main__":
    main()
