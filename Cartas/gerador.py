import os
import json
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Pergunta ao utilizador o nome do ficheiro JSON a utilizar
file_path = input("Digite o ficheiro que pretende usar (não escrever extensões): ").strip()
file_path = file_path + ".json"

# Verifica se o ficheiro existe
if not os.path.exists(file_path):
    print("Ficheiro não encontrado. A sair.")
    exit(1)

# Abre o ficheiro JSON e carrega o seu conteúdo para a variável "base"
with open(file_path, "r", encoding="utf-8") as f:
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