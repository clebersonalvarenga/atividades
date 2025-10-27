import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

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

# ---------------- INTERFACE ---------------- #
biblioteca = Biblioteca()

def abrir_menu_principal():
    tela_inicial.destroy()
    criar_janela_principal()

def criar_janela_principal():
    root = tk.Tk()
    root.title("Bookish Bliss - Biblioteca")
    root.geometry("800x600")
    root.state('zoomed')  # 🔹 abre a janela principal em tela cheia
    root.configure(bg="#f2f2f2")

    tk.Label(root, text="Biblioteca Digital", font=("Helvetica", 22, "bold"), bg="#f2f2f2").pack(pady=20)

    frame = tk.Frame(root, bg="#f2f2f2")
    frame.pack(pady=10)

    tk.Label(frame, text="Título:", bg="#f2f2f2").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entrada_titulo = tk.Entry(frame, width=50)
    entrada_titulo.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame, text="Autor:", bg="#f2f2f2").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entrada_autor = tk.Entry(frame, width=50)
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

    quadro_listagem = tk.Frame(root, bg="#f2f2f2")
    quadro_listagem.pack(pady=5, fill="both", expand=True)

    colunas = ("Título", "Autor", "Disponível")
    tree = ttk.Treeview(quadro_listagem, columns=colunas, show="headings", selectmode="browse")
    for c in colunas:
        tree.heading(c, text=c)
        tree.column(c, anchor="w")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

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

    botoes_quadro = tk.Frame(root, bg="#f2f2f2")
    botoes_quadro.pack(pady=8)

    tk.Button(botoes_quadro, text="Emprestar", command=emprestar_selecionado, bg="#2196F3", fg="white", width=12).grid(row=0, column=0, padx=6)
    tk.Button(botoes_quadro, text="Devolver", command=devolver_selecionado, bg="#FF9800", fg="white", width=12).grid(row=0, column=1, padx=6)
    tk.Button(botoes_quadro, text="Sair", command=root.destroy, bg="#F44336", fg="white", width=12).grid(row=0, column=2, padx=6)

    atualizar_tree()
    root.mainloop()

# --- Tela inicial ---
tela_inicial = tk.Tk()
tela_inicial.title("Bookish Bliss")
tela_inicial.geometry("600x400")
tela_inicial.state('zoomed')  # 🔹 abre a tela inicial em tela cheia
tela_inicial.configure(bg="#f2f2f2")

tk.Label(tela_inicial, text="Bookish Bliss 📚", font=("Helvetica", 36, "bold"), bg="#f2f2f2").pack(pady=100)
tk.Label(tela_inicial, text="Bem-vindo à sua biblioteca digital!", font=("Helvetica", 14), bg="#f2f2f2").pack(pady=10)

botao_entrar = tk.Button(
    tela_inicial, text="Entrar", command=abrir_menu_principal,
    bg="#1a73e8", fg="white", font=("Helvetica", 14, "bold"), width=12
)
botao_entrar.place(relx=0.5, rely=0.7, anchor="center")

tela_inicial.mainloop()
