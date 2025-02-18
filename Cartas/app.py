import streamlit as st
import json

# Lists to store attack and defense cards
if "cards_attack" not in st.session_state:
    st.session_state["cards_attack"] = []
if "cards_defense" not in st.session_state:
    st.session_state["cards_defense"] = []
if "deck" not in st.session_state:
    st.session_state["deck"] = ""

def add_card():
    deck = st.session_state["deck"].strip()
    title = st.session_state["title"].strip()
    card_type = st.session_state["card_type"].strip().lower()
    description = st.session_state["description"].strip()
    quote = st.session_state["quote"].strip()
    image_file = st.session_state["image"]
    image_name = image_file.name if image_file else ""

    if not title or card_type not in ["ataque", "defesa"] or not description:
        st.error("Título, Tipo (ataque/defesa) e descrição são necessários.")
        return

    card = {
        "deck": deck,
        "title": title,
        "state": "draft/ready",
        "image": image_name,
        "description": description,
        "quote": quote
    }

    if card_type == "ataque":
        st.session_state["cards_attack"].append(card)
    else:
        st.session_state["cards_defense"].append(card)
    
    st.success(f"Carta '{title}' adicionada com sucesso!")

def generate_json():
    json_data = {
        "flavors": {
            "attack": {"base_image": "templates/attackcard.png", "cards": st.session_state["cards_attack"]},
            "defense": {"base_image": "templates/defensecard.png", "cards": st.session_state["cards_defense"]}
        }
    }
    json_filename = "cartas.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    st.success("JSON gerado com sucesso!")
    st.download_button("Baixar JSON", json.dumps(json_data, ensure_ascii=False, indent=4), json_filename, "application/json")

# Streamlit UI
st.title("Criador de Cartas de Cibersegurança")

st.session_state["deck"] = st.text_input("Deck", value=st.session_state["deck"])
st.session_state["title"] = st.text_input("Título")
st.session_state["card_type"] = st.selectbox("Tipo", ["Ataque", "Defesa"])
st.session_state["description"] = st.text_area("Descrição")
st.session_state["quote"] = st.text_area("Quote")
st.session_state["image"] = st.file_uploader("Upload de Imagem", type=["png", "jpg", "jpeg"])

if st.button("Adicionar Carta"):
    add_card()

st.subheader("Cartas de Ataque")
if st.session_state["cards_attack"]:
    for card in st.session_state["cards_attack"]:
        st.text(f"- {card['title']}")
else:
    st.text("Nenhuma carta de ataque adicionada.")

st.subheader("Cartas de Defesa")
if st.session_state["cards_defense"]:
    for card in st.session_state["cards_defense"]:
        st.text(f"- {card['title']}")
else:
    st.text("Nenhuma carta de defesa adicionada.")

if st.button("Gerar JSON"):
    generate_json()
