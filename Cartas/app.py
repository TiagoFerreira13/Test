import streamlit as st
import json
import os

def main():
    st.title("Criador de Cartas de Cibersegurança")
    
    # Session state to store cards
    if "cards_attack" not in st.session_state:
        st.session_state["cards_attack"] = []
    if "cards_defense" not in st.session_state:
        st.session_state["cards_defense"] = []
    
    # Card Input Fields
    deck = st.text_input("Deck")
    title = st.text_input("Título")
    card_type = st.selectbox("Tipo", ["Ataque", "Defesa"])
    description = st.text_area("Descrição")
    quote = st.text_area("Quote (Opcional)")
    image = st.file_uploader("Upload de Imagem (Opcional)", type=["png", "jpg", "jpeg"])
    
    if st.button("Adicionar Carta"):
        if not title or not description:
            st.error("O título e a descrição são obrigatórios!")
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
    
    # Display cards
    st.subheader("Cartas de Ataque")
    for card in st.session_state["cards_attack"]:
        st.text(f"- {card['title']}")
    
    st.subheader("Cartas de Defesa")
    for card in st.session_state["cards_defense"]:
        st.text(f"- {card['title']}")
    
    # JSON Generation
    if st.button("Gerar JSON"):
        json_data = {
            "flavors": {
                "attack": {"base_image": "templates/attackcard.png", "cards": st.session_state["cards_attack"]},
                "defense": {"base_image": "templates/defensecard.png", "cards": st.session_state["cards_defense"]}
            },
            "font": {
                "path": "Rajdhani/Rajdhani-Regular.ttf",
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

if __name__ == "__main__":
    main()
