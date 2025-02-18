import streamlit as st
import json
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageOps

def main():
    st.title("Criador de Cartas de Cibersegurança")
    
    # Session state to store cards
    if "cards_attack" not in st.session_state:
        st.session_state["cards_attack"] = []
    if "cards_defense" not in st.session_state:
        st.session_state["cards_defense"] = []
    if "deck" not in st.session_state:
        st.session_state["deck"] = ""
    
    # Card Input Fields
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
            
            # Reset input fields except deck
            st.session_state["deck"] = deck.strip()
            st.experimental_rerun()
    
    # Display cards
    st.subheader("Cartas de Ataque")
    for card in st.session_state["cards_attack"]:
        st.text(f"- {card['title']}")
    
    st.subheader("Cartas de Defesa")
    for card in st.session_state["cards_defense"]:
        st.text(f"- {card['title']}")
    
    # JSON & Image Generation
    if st.button("Baixar Cartas e JSON"):
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
        
        # Create Images
        for flavor in ["attack", "defense"]:
            template_path = json_data["flavors"][flavor]["base_image"]
            cards = json_data["flavors"][flavor]["cards"]
            
            for card in cards:
                template = Image.open(template_path).convert("RGBA")
                draw = ImageDraw.Draw(template)
                title_font = ImageFont.truetype("Rajdhani/Rajdhani-Regular.ttf", 48)
                draw.text((100, 50), card["title"], font=title_font, fill=(255,255,255))
                image_filename = f"{card['deck'].replace(' ', '_')}_{card['title'].replace(' ', '_')}.png"
                template.save(image_filename)
                st.download_button(f"Baixar {card['title']}", open(image_filename, "rb"), image_filename, "image/png")

if __name__ == "__main__":
    main()
