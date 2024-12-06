import tkinter as tk
from tkinter import Toplevel, messagebox
from tkinter import ttk
import sqlite3

# Função para criar o banco de dados e a tabela
def criar_banco():
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    quantidade INTEGER NOT NULL)''')
    conn.commit()
    conn.close()

# Função para atualizar a lista de produtos
def atualizar_lista(ordem_coluna=None, reverso=False):
    for i in tree.get_children():
        tree.delete(i)

    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT * FROM produtos')
    produtos = c.fetchall()
    conn.close()

    # Ordena a lista de produtos, se necessário
    if ordem_coluna is not None:
        produtos.sort(key=lambda x: x[ordem_coluna], reverse=reverso)

    # Insere os produtos na tabela com linhas intercaladas
    for index, produto in enumerate(produtos):
        tag = "even" if index % 2 == 0 else "odd"
        tree.insert("", "end", iid=produto[0], values=produto, tags=(tag,))

# Adicionar funcionalidade de ordenação ao clicar nos cabeçalhos das colunas
def ordenar_por_coluna(coluna):
    global ordem_reversa
    ordem_reversa[coluna] = not ordem_reversa.get(coluna, False)
    atualizar_lista(ordem_coluna=coluna, reverso=ordem_reversa[coluna])

# Funções para CRUD
def adicionar_produto(entry_nome, entry_quantidade, janela_adicionar):
    nome = entry_nome.get()
    quantidade = entry_quantidade.get()

    if nome and quantidade.isdigit():
        conn = sqlite3.connect('estoque.db')
        c = conn.cursor()
        c.execute('INSERT INTO produtos (nome, quantidade) VALUES (?, ?)', (nome, int(quantidade)))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
        atualizar_lista()
        janela_adicionar.destroy()
    else:
        messagebox.showerror("Erro", "Preencha todos os campos corretamente!")

def tela_adicionar():
    janela_adicionar = Toplevel(root)
    janela_adicionar.title("Adicionar Produto")

    tk.Label(janela_adicionar, text="Nome do Produto").grid(row=0, column=0, padx=10, pady=10)
    tk.Label(janela_adicionar, text="Quantidade Inicial").grid(row=1, column=0, padx=10, pady=10)

    entry_nome = tk.Entry(janela_adicionar)
    entry_nome.grid(row=0, column=1, padx=10, pady=10)

    entry_quantidade = tk.Entry(janela_adicionar)
    entry_quantidade.grid(row=1, column=1, padx=10, pady=10)

    tk.Button(janela_adicionar, text="Adicionar", command=lambda: adicionar_produto(entry_nome, entry_quantidade, janela_adicionar)).grid(row=2, column=0, columnspan=2, pady=20)

def editar_produto():
    selecionado = tree.focus()
    if not selecionado:
        messagebox.showerror("Erro", "Selecione um produto para editar.")
        return

    id_produto = tree.item(selecionado)["values"][0]

    janela_editar = Toplevel(root)
    janela_editar.title("Editar Produto")

    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT * FROM produtos WHERE id = ?', (id_produto,))
    produto = c.fetchone()
    conn.close()

    tk.Label(janela_editar, text="Nome do Produto").grid(row=0, column=0, padx=10, pady=10)
    tk.Label(janela_editar, text="Quantidade").grid(row=1, column=0, padx=10, pady=10)

    entry_nome = tk.Entry(janela_editar)
    entry_nome.grid(row=0, column=1, padx=10, pady=10)
    entry_nome.insert(0, produto[1])

    entry_quantidade = tk.Entry(janela_editar)
    entry_quantidade.grid(row=1, column=1, padx=10, pady=10)
    entry_quantidade.insert(0, produto[2])

    def salvar_alteracoes():
        nome = entry_nome.get()
        quantidade = entry_quantidade.get()
        if nome and quantidade.isdigit():
            conn = sqlite3.connect('estoque.db')
            c = conn.cursor()
            c.execute('UPDATE produtos SET nome = ?, quantidade = ? WHERE id = ?',
                      (nome, int(quantidade), id_produto))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Produto editado com sucesso!")
            atualizar_lista()
            janela_editar.destroy()
        else:
            messagebox.showerror("Erro", "Preencha todos os campos corretamente!")

    tk.Button(janela_editar, text="Salvar Alterações", command=salvar_alteracoes).grid(row=2, column=0, columnspan=2, pady=20)

def excluir_produto():
    selecionado = tree.focus()
    if not selecionado:
        messagebox.showerror("Erro", "Selecione um produto para excluir.")
        return

    id_produto = tree.item(selecionado)["values"][0]

    resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este produto?")
    if resposta:
        conn = sqlite3.connect('estoque.db')
        c = conn.cursor()
        c.execute('DELETE FROM produtos WHERE id = ?', (id_produto,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
        atualizar_lista()

def gerenciar_estoque():
    selecionado = tree.focus()
    if not selecionado:
        messagebox.showerror("Erro", "Selecione um produto para gerenciar o estoque.")
        return

    id_produto = tree.item(selecionado)["values"][0]

    janela_estoque = Toplevel(root)
    janela_estoque.title("Gerenciar Estoque")

    tk.Label(janela_estoque, text="Adicionar ao Estoque").grid(row=0, column=0, padx=10, pady=10)
    entry_adicionar = tk.Entry(janela_estoque)
    entry_adicionar.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(janela_estoque, text="Retirar do Estoque").grid(row=1, column=0, padx=10, pady=10)
    entry_retirar = tk.Entry(janela_estoque)
    entry_retirar.grid(row=1, column=1, padx=10, pady=10)

    def atualizar_quantidade():
        adicionar = entry_adicionar.get()
        retirar = entry_retirar.get()

        if (adicionar.isdigit() or retirar.isdigit()):
            conn = sqlite3.connect('estoque.db')
            c = conn.cursor()

            if adicionar.isdigit():
                c.execute('UPDATE produtos SET quantidade = quantidade + ? WHERE id = ?', (int(adicionar), id_produto))
            if retirar.isdigit():
                c.execute('UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?', (int(retirar), id_produto))

            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Estoque atualizado com sucesso!")
            atualizar_lista()
            janela_estoque.destroy()
        else:
            messagebox.showerror("Erro", "Digite um valor válido para entrada ou saída!")

    tk.Button(janela_estoque, text="Atualizar Estoque", command=atualizar_quantidade).grid(row=2, column=0, columnspan=2, pady=20)

# Interface gráfica com Tkinter
root = tk.Tk()
root.title("Gestão de Estoque")
root.geometry("1280x720")

# Configuração do grid para expandir tabela
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Frame para os botões à esquerda
frame_botao_lateral = tk.Frame(root, bg="#f0f0f0")
frame_botao_lateral.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

# Função para realizar a pesquisa
def pesquisar_produto():
    termo = entry_pesquisa.get().strip().lower()
    for i in tree.get_children():
        tree.delete(i)

    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()
    c.execute('SELECT * FROM produtos WHERE LOWER(nome) LIKE ?', (f'%{termo}%',))
    produtos = c.fetchall()
    conn.close()

    for index, produto in enumerate(produtos):
        tag = "even" if index % 2 == 0 else "odd"
        tree.insert("", "end", iid=produto[0], values=produto, tags=(tag,))


# Separador
ttk.Separator(frame_botao_lateral, orient="horizontal").grid(row=6, column=0, sticky="ew", pady=15)

# Campo de pesquisa na barra lateral
label_pesquisa = tk.Label(frame_botao_lateral, text="Pesquisar Produto", 
                          bg="#f0f0f0", fg="#333", font=("Arial", 10, "italic"))
label_pesquisa.grid(row=7, column=0, padx=10, pady=(20, 5))

entry_pesquisa = tk.Entry(frame_botao_lateral, font=("Arial", 12), width=20)
entry_pesquisa.grid(row=8, column=0, padx=10, pady=5)

btn_pesquisar = tk.Button(frame_botao_lateral, text="Pesquisar", command=pesquisar_produto, 
                          relief="flat", bg="#007acc", fg="white", activebackground="#005f99", 
                          activeforeground="white", font=("Arial", 12), width=20, padx=10, pady=5)
btn_pesquisar.grid(row=9, column=0, pady=10)

# Botões
btn_style = {"relief": "flat", "bg": "#007acc", "fg": "white", "activebackground": "#005f99", 
             "activeforeground": "white", "font": ("Arial", 12), "width": 20, "padx": 10, "pady": 5}
tk.Button(frame_botao_lateral, text="Adicionar Produto", command=tela_adicionar, **btn_style).grid(row=0, column=0, pady=10)

# Separador
ttk.Separator(frame_botao_lateral, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=15)

# Mensagem de instrução
label_instrucao = tk.Label(frame_botao_lateral, text="Selecione um produto para editar, apagar ou gerir estoque", wraplength=180, justify="center", bg="#f0f0f0", fg="#333", font=("Arial", 10, "italic"))
label_instrucao.grid(row=2, column=0, padx=10, pady=(10, 20))

# Botões de ação
tk.Button(frame_botao_lateral, text="Editar Produto", command=editar_produto, **btn_style).grid(row=3, column=0, pady=10)
tk.Button(frame_botao_lateral, text="Apagar Produto", command=excluir_produto, **btn_style).grid(row=4, column=0, pady=10)
tk.Button(frame_botao_lateral, text="Gerenciar Estoque", command=gerenciar_estoque, **btn_style).grid(row=5, column=0, pady=10)

# Configurando o estilo da tabela
style = ttk.Style()
style.configure("Treeview", font=("Arial", 12), rowheight=30, background="white", fieldbackground="white")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
style.map("Treeview", background=[("selected", "#007acc")])  # Cor da linha selecionada
style.configure("Treeview", bordercolor="#cfcfcf")

# Tabela para exibir os produtos (Treeview)
tree = ttk.Treeview(root, columns=("ID", "Nome", "Quantidade"), show="headings", style="Treeview")
tree.heading("ID", text="ID", command=lambda: ordenar_por_coluna(0))
tree.heading("Nome", text="Nome", command=lambda: ordenar_por_coluna(1))
tree.heading("Quantidade", text="Quantidade", command=lambda: ordenar_por_coluna(2))
tree.column("ID", width=50, anchor="center")
tree.column("Nome", anchor="w")
tree.column("Quantidade", width=100, anchor="center")
tree.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Configura tags para linhas intercaladas
tree.tag_configure("even", background="white")
tree.tag_configure("odd", background="#f1f1f1")

# Dicionário para controlar ordem reversa na ordenação
ordem_reversa = {}

# Inicializar banco de dados e atualizar lista
criar_banco()
atualizar_lista()

root.mainloop()
