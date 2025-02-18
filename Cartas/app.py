import streamlit as st
import json
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageOps

def draw_text(draw, text, font, box, align="left", fill=(255,255,255)):
    x, y, w, h = box
    wrap_width = 30 if align == "center" else 40
    lines = textwrap.wrap(text, width=wrap_width)
    bbox_ref = draw.textbbox((0, 0), "A", font=font)
    line_height = (bbox_ref[3] - bbox_ref[1]) + 6
    current_y = y
    for line in lines:
        line_bbox = draw.textbbox((0,0), line, font=font)
        line_width = line_bbox[2] - line_bbox[0]
        line_x = x + (w - line_width) // 2 if align == "center" else x
        draw.text((line_x, current_y), line, font=font, fill=fill)
        current_y += line_height

def create_card_images(json_data):
    image_filenames = []
    for flavor in ["attack", "defense"]:
        template_path = json_data["flavors"][flavor]["base_image"]
        cards = json_data["flavors"][flavor]["cards"]
        for card in cards:
            template = Image.open(template_path).convert("RGBA")
            draw = ImageDraw.Draw(template)
            title_font = ImageFont.truetype("Rajdhani/Rajdhani-Regular.ttf", 48)
            draw_text(draw, card["title"], title_font, (100, 50, 400, 60), align="center")
            image_filename = f"{card['deck'].replace(' ', '_')}_{card['title'].replace(' ', '_')}.png"
            template.save(image_filename)
            image_filenames.append(image_filename)
    return image_filenames

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
    quote = st.text_area("Quote (Opcional)")
    image = st.file_uploader("Upload de Imagem (Opcional)", type=["png", "jpg", "jpeg"])
    
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
    
    if st.button("Baixar JSON"):
        json_data = {
            "flavors": {
                "attack": {"base_image": "templates/attackcard.png", "cards": st.session_state["cards_attack"]},
                "defense": {"base_image": "templates/defensecard.png", "cards": st.session_state["cards_defense"]}
            }
        }
        json_filename = "cartas.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        st.download_button("Baixar JSON", json.dumps(json_data, ensure_ascii=False, indent=4), json_filename, "application/json")
    
    if st.button("Baixar Cartas"):
        json_data = {
            "flavors": {
                "attack": {"base_image": "templates/attackcard.png", "cards": st.session_state["cards_attack"]},
                "defense": {"base_image": "templates/defensecard.png", "cards": st.session_state["cards_defense"]}
            }
        }
        image_filenames = create_card_images(json_data)
        for image_filename in image_filenames:
            st.download_button(f"Baixar {image_filename}", open(image_filename, "rb"), image_filename, "image/png")

if __name__ == "__main__":
    main()
