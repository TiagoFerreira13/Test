import customtkinter as ctk
from tkinter import filedialog, messagebox
import json

# Listas para armazenar as cartas de ataque e defesa
cards_attack = []
cards_defense = []

def add_card():
    deck = entry_deck.get().strip()
    title = entry_title.get().strip()
    card_type = combo_type.get().strip().lower()
    description = text_description.get("1.0", ctk.END).strip()
    quote = text_quote.get("1.0", ctk.END).strip()
    image_path = entry_image.get().strip()  # caminho da imagem (opcional)

    if not title or card_type not in ["ataque", "defesa"] or not description:
        messagebox.showerror("Erro!", "Título, Tipo (ataque/defesa) e descrição são necessários.")
        return

    # Cria a carta com as chaves desejadas
    card = {
        "deck": deck,
        "title": title,
        "state": "draft/ready",
        "image": image_path if image_path else "images/",
        "description": description,
        "quote": quote
    }

    if card_type == "ataque":
        cards_attack.append(card)
        listbox_attack.configure(state="normal")
        listbox_attack.insert(ctk.END, title + "\n")
        listbox_attack.configure(state="disabled")
    else:
        cards_defense.append(card)
        listbox_defense.configure(state="normal")
        listbox_defense.insert(ctk.END, title + "\n")
        listbox_defense.configure(state="disabled")

    # Limpa os campos de entrada
    entry_title.delete(0, ctk.END)
    combo_type.set("")
    entry_image.delete(0, ctk.END)
    text_description.delete("1.0", ctk.END)
    text_quote.delete("1.0", ctk.END)

def browse_image():
    file_path = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif"), ("All Files", "*.*")]
    )
    if file_path:
        entry_image.delete(0, ctk.END)
        entry_image.insert(0, file_path)

def generate_json():
    # Estrutura JSON conforme especificado
    base_data = {
        "flavors": {
            "attack": {
                "base_image": "templates/attackcard.png",
                "cards": cards_attack
            },
            "defense": {
                "base_image": "templates/defensecard.png",
                "cards": cards_defense
            }
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
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        title="Salvar JSON"
    )
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(base_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Sucesso", f"Arquivo JSON gerado em:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o arquivo:\n{e}")

# Configura a aparência e o tema moderno
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Cria a janela principal
root = ctk.CTk()
root.title("Creador de cartas")
root.geometry("900x850")

# Frame para os campos de entrada
frame_inputs = ctk.CTkFrame(root, corner_radius=10)
frame_inputs.pack(padx=20, pady=20, fill="x")

# Deck
label_deck = ctk.CTkLabel(frame_inputs, text="Deck:")
label_deck.grid(row=0, column=0, padx=10, pady=10, sticky="w")
entry_deck = ctk.CTkEntry(frame_inputs, width=400)
entry_deck.grid(row=0, column=1, padx=10, pady=10)

# Título
label_title = ctk.CTkLabel(frame_inputs, text="Título:")
label_title.grid(row=1, column=0, padx=10, pady=10, sticky="w")
entry_title = ctk.CTkEntry(frame_inputs, width=400)
entry_title.grid(row=1, column=1, padx=10, pady=10)

# Caminho da Imagem (opcional) com botão de Procurar
label_image = ctk.CTkLabel(frame_inputs, text="Imagem (opcional):")
label_image.grid(row=2, column=0, padx=10, pady=10, sticky="w")
entry_image = ctk.CTkEntry(frame_inputs, width=400)
entry_image.grid(row=2, column=1, padx=10, pady=10)
btn_browse = ctk.CTkButton(frame_inputs, text="Procurar", command=browse_image)
btn_browse.grid(row=2, column=2, padx=10, pady=10)

# Tipo (ataque/defesa)
label_type = ctk.CTkLabel(frame_inputs, text="Tipo:")
label_type.grid(row=3, column=0, padx=10, pady=10, sticky="w")
combo_type = ctk.CTkOptionMenu(frame_inputs,width = 400, values=["ataque", "defesa"])
combo_type.grid(row=3, column=1, padx=10, pady=10)

# Descrição
label_description = ctk.CTkLabel(frame_inputs, text="Descrição:")
label_description.grid(row=4, column=0, padx=10, pady=10, sticky="nw")
text_description = ctk.CTkTextbox(frame_inputs, width=400, height=100)
text_description.grid(row=4, column=1, padx=10, pady=10)

# Quote
label_quote = ctk.CTkLabel(frame_inputs, text="Quote:")
label_quote.grid(row=5, column=0, padx=10, pady=10, sticky="nw")
text_quote = ctk.CTkTextbox(frame_inputs, width=400, height=60)
text_quote.grid(row=5, column=1, padx=10, pady=10)

# Botão para adicionar carta
btn_add = ctk.CTkButton(frame_inputs, text="Adicionar Carta", command=add_card)
btn_add.grid(row=6, column=0, padx=10, pady=10, sticky="e")

# Frame para exibir as cartas criadas
frame_lists = ctk.CTkFrame(root, corner_radius=10)
frame_lists.pack(padx=10, pady=10, fill="both", expand=True)

# Caixa para cartas de ataque (somente leitura)
frame_attack = ctk.CTkFrame(frame_lists, corner_radius=10)
frame_attack.pack(side="left", padx=10, pady=10, fill="both", expand=True)
label_attack = ctk.CTkLabel(frame_attack, text="Cartas de ataque")
label_attack.pack(padx=10, pady=10)
listbox_attack = ctk.CTkTextbox(frame_attack)
listbox_attack.pack(padx=10, pady=10, fill="both", expand=True)
listbox_attack.configure(state="disabled")

# Caixa para cartas de defesa (somente leitura)
frame_defense = ctk.CTkFrame(frame_lists, corner_radius=10)
frame_defense.pack(side="left", padx=10, pady=10, fill="both", expand=True)
label_defense = ctk.CTkLabel(frame_defense, text="Cartas de defesa")
label_defense.pack(padx=10, pady=10)
listbox_defense = ctk.CTkTextbox(frame_defense)
listbox_defense.pack(padx=10, pady=10, fill="both", expand=True)
listbox_defense.configure(state="disabled")

# Botão para gerar JSON
btn_generate = ctk.CTkButton(root, text="Gerar JSON", command=generate_json)
btn_generate.pack(pady=20)

root.mainloop()
