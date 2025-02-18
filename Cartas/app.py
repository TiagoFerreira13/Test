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
            
            # Reset input fields except deck
            st.session_state["deck"] = deck.strip()
    
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
        if  st.button("Gerar Cartas"):
            # Abre o ficheiro JSON e carrega o seu conteúdo para a variável "base"
            with open(json_filename, "r", encoding="utf-8") as f:
                base = json.load(f)

            # Obtém as configurações do JSON
            font_conf = base["font"]
            layout = base["layout"]
            output_dir = base["output_dir"]

            # Carrega as fontes conforme os tamanhos definidos no JSON
            title_font = ImageFont.truetype(font_conf["path"], font_conf["title_size"])
            category_font = ImageFont.truetype(font_conf["path"], font_conf["category_size"])
            desc_font = ImageFont.truetype(font_conf["path"], font_conf["desc_size"])

            # Função para escrever texto na imagem
            def draw_text(draw, text, font, box, align="left", fill=(255,255,255)):
                x, y, w, h = box
                wrap_width = 30 if align == "center" else 40  # Define o número de caracteres por linha
                lines = textwrap.wrap(text, width=wrap_width) # Divide o texto em linhas
                bbox_ref = draw.textbbox((0, 0), "A", font=font) # Mede a altura da linha do texto
                line_height = (bbox_ref[3] - bbox_ref[1]) + 6 # Define a altura da linha e adiciona espaçameto entre linhas
                current_y = y
                # Para texto justificado, calcula os espaços entre palavras
                for i, line in enumerate(lines):
                    if align == "justified" and i < len(lines) - 1:
                        words = line.split()
                        if len(words) == 1:
                            single_bbox = draw.textbbox((0, 0), line, font=font)
                            lw = single_bbox[2] - single_bbox[0]
                            line_x = x + (w - lw) // 2
                            draw.text((line_x, current_y), line, font=font, fill=fill)
                        else:
                            total_words_width = sum(draw.textbbox((0,0), word, font=font)[2] for word in words)
                            total_space = w - total_words_width
                            space_count = len(words) - 1
                            space_width = total_space // space_count if space_count > 0 else 0
                            current_x = x
                            for j, word in enumerate(words):
                                draw.text((current_x, current_y), word, font=font, fill=fill)
                                wbbox = draw.textbbox((0,0), word, font=font)
                                word_width = wbbox[2] - wbbox[0]
                                current_x += word_width
                                if j < len(words) - 1:
                                    current_x += space_width
                    # Para o texto centrado
                    else:
                        line_bbox = draw.textbbox((0,0), line, font=font)
                        line_width = line_bbox[2] - line_bbox[0]
                        if align == "center":
                            line_x = x + (w - line_width) // 2
                        else:
                            line_x = x
                        draw.text((line_x, current_y), line, font=font, fill=fill)
                    current_y += line_height
            # Criação de cartas
            for flavor in ["attack", "defense"]:
                if flavor == "attack":
                    template_path = base["flavors"]["attack"]["base_image"]
                    category_label = "Ataque"
                else:
                    template_path = base["flavors"]["defense"]["base_image"]
                    category_label = "Defesa"

                cards = base["flavors"][flavor]["cards"]
                for card in cards:
                    template = Image.open(template_path).convert("RGBA")
                    draw = ImageDraw.Draw(template)

                    # Converte coordenadas do JSON para tuplos
                    title_box = tuple(layout["title_box"])
                    image_box = tuple(layout["image_box"])
                    category_box = tuple(layout["category_box"])
                    desc_box = tuple(layout["desc_box"])
                    quote_box = tuple(layout["quote_box"])

                    # Desenha o titulo centrado 
                    draw_text(draw, card["title"], title_font, title_box, align="center")

                    # Se tiver uma imagem abre e ajusta-a
                    if card.get("image") and os.path.exists(card["image"]):
                        x_img, y_img, box_w, box_h = image_box
                        card_image = Image.open(card["image"]).convert("RGBA")
                        card_image = ImageOps.fit(card_image, (int(box_w), int(box_h)), Image.Resampling.LANCZOS)
                        template.paste(card_image, (x_img, y_img), card_image)

                    # Desenha a categoria
                    draw_text(draw, category_label, category_font, category_box, align="left")

                    # Desenha a descrição justificada
                    draw_text(draw, card["description"], desc_font, desc_box, align="justified")

                    # Desenha uma quote justificada
                    if card.get("quote") and card["quote"].strip():
                        draw_text(draw, card["quote"], desc_font, quote_box, align="justified")

                    # Imprime a carta
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    deck = card["deck"].strip()
                    filename = deck.replace(" ", "_") + "_" + card["title"].replace(" ", "_") + ".png"
                    output_path = os.path.join(output_dir, filename)
                    template.save(output_path)
                    print(f"Carta gerada: {output_path}")

if __name__ == "__main__":
    main()
