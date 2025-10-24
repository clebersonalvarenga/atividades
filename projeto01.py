# biblioteca_gui_robusto.py
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

# tenta importar Pillow, se não tiver, usaremos fallback
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# ---------------- CLASSES ---------------- #
class Livro:
    def __init__(self, titulo, autor, disponivel=True):
        self.titulo = titulo
        self.autor = autor
        self.disponivel = disponivel

    def emprestar(self):
        if self.disponivel:
            self.disponivel = False
            return True, f"O livro '{self.titulo}' foi emprestado com sucesso!"
        return False, f"O livro '{self.titulo}' já está emprestado."

    def devolver(self):
        if not self.disponivel:
            self.disponivel = True
            return True, f"O livro '{self.titulo}' foi devolvido com sucesso!"
        return False, f"O livro '{self.titulo}' já estava disponível."

    def to_dict(self):
        return {"titulo": self.titulo, "autor": self.autor, "disponivel": self.disponivel}

    def __str__(self):
        status = "Disponível" if self.disponivel else "Emprestado"
        return f"{self.titulo} - {self.autor} ({status})"


class Biblioteca:
    def __init__(self, arquivo="biblioteca.json"):
        self.arquivo = arquivo
        self.livros = []
        self.carregar_dados()

    def adicionar_livro(self, livro):
        self.livros.append(livro)
        self.salvar_dados()

    def salvar_dados(self):
        try:
            with open(self.arquivo, "w", encoding="utf-8") as f:
                json.dump([livro.to_dict() for livro in self.livros], f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erro ao salvar", f"Não foi possível salvar os dados:\n{e}")

    def carregar_dados(self):
        if not os.path.exists(self.arquivo):
            self.livros = []
            return
        try:
            with open(self.arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()
                if conteudo == "":
                    self.livros = []
                    return
                dados = json.loads(conteudo)
                self.livros = []
                for item in dados:
                    # tolerância: se faltar chave, usa valores padrão
                    titulo = item.get("titulo", "Título sem nome")
                    autor = item.get("autor", "Autor desconhecido")
                    disponivel = item.get("disponivel", True)
                    self.livros.append(Livro(titulo, autor, disponivel))
        except json.JSONDecodeError:
            messagebox.showwarning("JSON inválido", "O arquivo biblioteca.json está inválido. Ignorando o conteúdo.")
            self.livros = []
        except Exception as e:
            messagebox.showerror("Erro ao carregar", f"Erro ao ler arquivo:\n{e}")
            self.livros = []

# ---------------- Interface ---------------- #
biblioteca = Biblioteca()

def abrir_menu_principal():
    tela_inicial.destroy()
    criar_janela_principal()

def criar_janela_principal():
    root = tk.Tk()
    root.title("Bookish Bliss - Biblioteca")
    root.geometry("600x450")
    root.configure(bg="#f2f2f2")

    tk.Label(root, text="Biblioteca Digital", font=("Helvetica", 18, "bold"), bg="#f2f2f2").pack(pady=10)

    frame = tk.Frame(root, bg="#f2f2f2")
    frame.pack(pady=5)

    tk.Label(frame, text="Título:", bg="#f2f2f2").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entrada_titulo = tk.Entry(frame, width=40)
    entrada_titulo.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame, text="Autor:", bg="#f2f2f2").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entrada_autor = tk.Entry(frame, width=40)
    entrada_autor.grid(row=1, column=1, padx=5, pady=5)

    def adicionar_livro_interface():
        titulo = entrada_titulo.get().strip()
        autor = entrada_autor.get().strip()
        if titulo and autor:
            biblioteca.adicionar_livro(Livro(titulo, autor))
            atualizar_tree()
            messagebox.showinfo("Sucesso", f"Livro '{titulo}' cadastrado!")
            entrada_titulo.delete(0, tk.END)
            entrada_autor.delete(0, tk.END)
        else:
            messagebox.showwarning("Atenção", "Preencha todos os campos!")

    tk.Button(root, text="Cadastrar Livro", command=adicionar_livro_interface, bg="#3a7bd5", fg="white", width=20).pack(pady=8)

    # Treeview para listar livros (Título, Autor, Disponível)
    quadro_listagem = tk.Frame(root, bg="#f2f2f2")
    quadro_listagem.pack(pady=5, fill="both", expand=True)

    colunas = ("Título", "Autor", "Disponível")
    tree = ttk.Treeview(quadro_listagem, columns=colunas, show="headings", selectmode="browse")
    for c in colunas:
        tree.heading(c, text=c)
        tree.column(c, anchor="w")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Scrollbar vertical
    vsb = ttk.Scrollbar(quadro_listagem, orient="vertical", command=tree.yview)
    tree.configure(yscroll=vsb.set)
    vsb.pack(side="right", fill="y")

    def atualizar_tree():
        for i in tree.get_children():
            tree.delete(i)
        for livro in biblioteca.livros:
            disponivel_text = "Sim" if livro.disponivel else "Não"
            tree.insert("", tk.END, values=(livro.titulo, livro.autor, disponivel_text))

    def emprestar_selecionado():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um livro na lista!")
            return
        idx = tree.index(sel[0])
        sucesso, msg = biblioteca.livros[idx].emprestar()
        if sucesso:
            biblioteca.salvar_dados()
        atualizar_tree()
        messagebox.showinfo("Resultado", msg)

    def devolver_selecionado():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um livro na lista!")
            return
        idx = tree.index(sel[0])
        sucesso, msg = biblioteca.livros[idx].devolver()
        if sucesso:
            biblioteca.salvar_dados()
        atualizar_tree()
        messagebox.showinfo("Resultado", msg)

    # botoes de ação
    botoes_quadro = tk.Frame(root, bg="#f2f2f2")
    botoes_quadro.pack(pady=8)

    tk.Button(botoes_quadro, text="Emprestar", command=emprestar_selecionado, bg="#2196F3", fg="white", width=12).grid(row=0, column=0, padx=6)
    tk.Button(botoes_quadro, text="Devolver", command=devolver_selecionado, bg="#FF9800", fg="white", width=12).grid(row=0, column=1, padx=6)
    tk.Button(botoes_quadro, text="Sair", command=root.destroy, bg="#F44336", fg="white", width=12).grid(row=0, column=2, padx=6)

    atualizar_tree()
    root.mainloop()

# --- Tela inicial (com imagem opcional) ---
tela_inicial = tk.Tk()
tela_inicial.title("Bookish Bliss")
tela_inicial.geometry("500x400")
tela_inicial.resizable(False, False)

IMAGE_NAME = "bookish_bliss.jpg"  # coloque o nome do arquivo da imagem aqui

# tenta carregar imagem com Pillow (quando disponível), senão usa label simples
if PIL_AVAILABLE and os.path.exists(IMAGE_NAME):
    try:
        img = Image.open(IMAGE_NAME)
        img = img.resize((500, 400))
        img_tk = ImageTk.PhotoImage(img)
        label_img = tk.Label(tela_inicial, image=img_tk)
        label_img.image = img_tk  # referencia para evitar garbage collection
        label_img.pack(fill="both", expand=True)
    except Exception as e:
        tk.Label(tela_inicial, text="Bookish Bliss", font=("Helvetica", 24, "bold")).pack(expand=True)
        print("Erro ao abrir imagem:", e)
else:
    # se Pillow não está disponível ou imagem não existe, mostra texto informativo
    if not PIL_AVAILABLE:
        aviso_text = "Imagem não mostrada (Pillow não instalado).\nInstale com: pip install pillow"
    else:
        aviso_text = f"Imagem '{IMAGE_NAME}' não encontrada na pasta do script."
    tk.Label(tela_inicial, text="Bookish Bliss", font=("Helvetica", 28, "bold")).pack(pady=60)
    tk.Label(tela_inicial, text=aviso_text, font=("Helvetica", 10)).pack()

botao_entrar = tk.Button(tela_inicial, text="Entrar", command=abrir_menu_principal,
                         bg="#1a73e8", fg="white", font=("Helvetica", 12, "bold"), width=10)
botao_entrar.place(relx=0.5, rely=0.8, anchor="center")

tela_inicial.mainloop()