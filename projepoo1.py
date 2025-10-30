import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

# ---------------- CLASSES ---------------- 
class Livro:
    def __init__(self, titulo, autor, disponivel=True):
        self.__titulo = titulo.strip().title()
        self.__autor = autor.strip().title()
        self.__disponivel = disponivel

    # Encapsulamento
    def get_titulo(self): return self.__titulo
    def get_autor(self): return self.__autor
    def is_disponivel(self): return self.__disponivel
    def set_disponivel(self, valor: bool): self.__disponivel = valor

    # Ações
    def emprestar(self):
        if self.__disponivel:
            self.__disponivel = False
            return True, f"O livro '{self.__titulo}' foi emprestado com sucesso!"
        return False, f"O livro '{self.__titulo}' já está emprestado."

    def devolver(self):
        if not self.__disponivel:
            self.__disponivel = True
            return True, f"O livro '{self.__titulo}' foi devolvido com sucesso!"
        return False, f"O livro '{self.__titulo}' já estava disponível."


    def to_dict(self):
        return {
            "titulo": self.__titulo,
            "autor": self.__autor,
            "disponivel": self.__disponivel,
            "tipo": "Livro"
        }

    
    def exibir_informacoes(self):
        return (self.__titulo, self.__autor, "Sim" if self.__disponivel else "Não", "Livro")


class LivroFisico(Livro):
    def to_dict(self):
        data = super().to_dict()
        data["tipo"] = "Físico"
        return data
    def exibir_informacoes(self):
        titulo, autor, disponivel, _ = super().exibir_informacoes()
        return (titulo, autor, disponivel, "Físico")


class LivroDigital(Livro):
    def to_dict(self):
        data = super().to_dict()
        data["tipo"] = "Digital"
        return data
    def exibir_informacoes(self):
        titulo, autor, disponivel, _ = super().exibir_informacoes()
        return (titulo, autor, disponivel, "Digital")



class Biblioteca:
    def __init__(self, arquivo="biblioteca.json"):
        self.__arquivo = arquivo
        self.__livros = []
        self.carregar_dados()

    def adicionar_livro(self, livro):
        self.__livros.append(livro)
        self.salvar_dados()

    def remover_livro(self, idx):
        if 0 <= idx < len(self.__livros):
            del self.__livros[idx]
            self.salvar_dados()

    def get_livros(self):
        return self.__livros

    def salvar_dados(self):
        try:
            with open(self.__arquivo, "w", encoding="utf-8") as f:
                json.dump([l.to_dict() for l in self.__livros], f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erro ao salvar", str(e))

    def carregar_dados(self):
        if not os.path.exists(self.__arquivo):
            self.__livros = []
            return
        try:
            with open(self.__arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()
                if not conteudo:
                    self.__livros = []
                    return
                dados_json = json.loads(conteudo)
                self.__livros = []
                for item in dados_json:
                    titulo = item.get("titulo", "")
                    autor = item.get("autor", "")
                    disponivel = item.get("disponivel", True)
                    tipo = item.get("tipo", "Livro")
                    if tipo == "Físico":
                        self.__livros.append(LivroFisico(titulo, autor, disponivel))
                    elif tipo == "Digital":
                        self.__livros.append(LivroDigital(titulo, autor, disponivel))
                    else:
                        self.__livros.append(Livro(titulo, autor, disponivel))
        except Exception as e:
            messagebox.showerror("Erro ao carregar", str(e))


# ---------------- INTERFACE ---------------- 
biblioteca = Biblioteca()

def abrir_janela_principal(root):
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Bookish Bliss - Biblioteca")
    frame = tk.Frame(root, bg="#f2f2f2")
    frame.place(relx=0.5, rely=0.05, anchor="n", relwidth=0.8)

    tk.Label(frame, text="Biblioteca Digital", font=("Helvetica", 22, "bold"), bg="#f2f2f2").pack(pady=20)

    
    frame_inputs = tk.Frame(frame, bg="#f2f2f2")
    frame_inputs.pack(pady=10, fill="x")

    tk.Label(frame_inputs, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entrada_titulo = tk.Entry(frame_inputs)
    entrada_titulo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(frame_inputs, text="Autor:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entrada_autor = tk.Entry(frame_inputs)
    entrada_autor.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(frame_inputs, text="Tipo:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    tipo_var = tk.StringVar(value="Físico")
    tk.OptionMenu(frame_inputs, tipo_var, "Físico", "Digital").grid(row=2, column=1, sticky="w", padx=5, pady=5)

    frame_inputs.grid_columnconfigure(1, weight=1)

    
    quadro_listagem = tk.Frame(frame, bg="#f2f2f2")
    quadro_listagem.pack(pady=5, fill="both", expand=True)
    colunas = ("Título", "Autor", "Disponível", "Tipo")
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
        for livro in biblioteca.get_livros():
            tree.insert("", tk.END, values=livro.exibir_informacoes())

    def adicionar_livro():
        titulo = entrada_titulo.get().strip()
        autor = entrada_autor.get().strip()
        tipo = tipo_var.get()
        if not titulo or not autor:
            messagebox.showwarning("Atenção", "Preencha título e autor")
            return
        if tipo == "Físico":
            livro = LivroFisico(titulo, autor)
        else:
            livro = LivroDigital(titulo, autor)
        biblioteca.adicionar_livro(livro)
        atualizar_tree()
        messagebox.showinfo("Sucesso", f"Livro '{titulo}' cadastrado!")
        entrada_titulo.delete(0, tk.END)
        entrada_autor.delete(0, tk.END)

    def emprestar():
        sel = tree.selection()
        if not sel: return messagebox.showwarning("Aviso", "Selecione um livro")
        idx = tree.index(sel[0])
        livro = biblioteca.get_livros()[idx]
        sucesso, msg = livro.emprestar()
        if sucesso: biblioteca.salvar_dados()
        atualizar_tree()
        messagebox.showinfo("Resultado", msg)

    def devolver():
        sel = tree.selection()
        if not sel: return messagebox.showwarning("Aviso", "Selecione um livro")
        idx = tree.index(sel[0])
        livro = biblioteca.get_livros()[idx]
        sucesso, msg = livro.devolver()
        if sucesso: biblioteca.salvar_dados()
        atualizar_tree()
        messagebox.showinfo("Resultado", msg)

    def remover():
        sel = tree.selection()
        if not sel: return messagebox.showwarning("Aviso", "Selecione um livro para remover")
        idx = tree.index(sel[0])
        livro = biblioteca.get_livros()[idx]
        confirm = messagebox.askyesno("Confirmação", f"Remover '{livro.get_titulo()}'?")
        if confirm:
            biblioteca.remover_livro(idx)
            atualizar_tree()
            messagebox.showinfo("Removido", f"Livro '{livro.get_titulo()}' removido!")

    
    botoes = tk.Frame(frame, bg="#f2f2f2")
    botoes.pack(pady=8)
    tk.Button(botoes, text="Cadastrar", command=adicionar_livro, bg="#3a7bd5", fg="white", width=12).grid(row=0, column=0, padx=5)
    tk.Button(botoes, text="Emprestar", command=emprestar, bg="#2196F3", fg="white", width=12).grid(row=0, column=1, padx=5)
    tk.Button(botoes, text="Devolver", command=devolver, bg="#FF9800", fg="white", width=12).grid(row=0, column=2, padx=5)
    tk.Button(botoes, text="Remover", command=remover, bg="#9C27B0", fg="white", width=12).grid(row=0, column=3, padx=5)
    tk.Button(botoes, text="Sair", command=root.destroy, bg="#F44336", fg="white", width=12).grid(row=0, column=4, padx=5)

    atualizar_tree()


root = tk.Tk()
root.title("Bookish Bliss")
root.state("zoomed")
root.configure(bg="#f2f2f2")

tk.Label(root, text="Bookish Bliss 📚", font=("Helvetica", 36, "bold"), bg="#f2f2f2").pack(pady=150)
tk.Button(root, text="Entrar", command=lambda: abrir_janela_principal(root),
          bg="#1a73e8", fg="white", font=("Helvetica", 14, "bold"), width=12).pack()

root.mainloop()