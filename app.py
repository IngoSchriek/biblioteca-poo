import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
import json
from bson import ObjectId

# Conexão com MongoDB
client = MongoClient('mongodb+srv://user:1234@aluguel-veiculos.pidirjm.mongodb.net/?retryWrites=true&w=majority&appName=aluguel-veiculos')
db = client['biblioteca']
collection = db['livros']

# Arquivo de dados local
data_file = 'livros.json'

# Função para converter ObjectId para string
def convert_object_id(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError

# Classes
class Livro:
    def __init__(self, titulo, autor, ano):
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
    
    def salvar(self):
        collection.insert_one(self.__dict__)
    
    def to_dict(self):
        return self.__dict__

class LivroDigital(Livro):
    def __init__(self, titulo, autor, ano, formato):
        super().__init__(titulo, autor, ano)
        self.formato = formato
    
    def to_dict(self):
        data = super().to_dict()
        data['formato'] = self.formato
        return data
        
class LivroFisico(Livro):
    def __init__(self, titulo, autor, ano, numero_paginas):
        super().__init__(titulo, autor, ano)
        self.numero_paginas = numero_paginas
    
    def to_dict(self):
        data = super().to_dict()
        data['numero_paginas'] = self.numero_paginas
        return data

class Biblioteca:
    def __init__(self):
        self.livros = []
        self.carregar_livros()
    
    def adicionar_livro(self, livro):
        self.livros.append(livro)
        livro.salvar()
        self.salvar_livros()
        
    def listar_livros(self):
        return list(collection.find())
    
    def salvar_livros(self):
        with open(data_file, 'w') as f:
            json.dump([livro.to_dict() for livro in self.livros], f, default=convert_object_id)
    
    def carregar_livros(self):
        try:
            with open(data_file, 'r') as f:
                livros_data = json.load(f)
                for livro_data in livros_data:
                    if 'formato' in livro_data:
                        livro = LivroDigital(livro_data['titulo'], livro_data['autor'], livro_data['ano'], livro_data['formato'])
                    elif 'numero_paginas' in livro_data:
                        livro = LivroFisico(livro_data['titulo'], livro_data['autor'], livro_data['ano'], livro_data['numero_paginas'])
                    else:
                        livro = Livro(livro_data['titulo'], livro_data['autor'], livro_data['ano'])
                    self.livros.append(livro)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

# Interface Gráfica
class BibliotecaInterface:
    def __init__(self, root):
        self.biblioteca = Biblioteca()
        self.root = root
        self.root.title("Sistema de Gerenciamento de Biblioteca")
        
        # Widgets
        self.titulo_label = tk.Label(root, text="Título")
        self.titulo_label.grid(row=0, column=0)
        self.titulo_entry = tk.Entry(root)
        self.titulo_entry.grid(row=0, column=1)
        
        self.autor_label = tk.Label(root, text="Autor")
        self.autor_label.grid(row=1, column=0)
        self.autor_entry = tk.Entry(root)
        self.autor_entry.grid(row=1, column=1)
        
        self.ano_label = tk.Label(root, text="Ano")
        self.ano_label.grid(row=2, column=0)
        self.ano_entry = tk.Entry(root)
        self.ano_entry.grid(row=2, column=1)
        
        self.formato_label = tk.Label(root, text="Formato (para Livro Digital)")
        self.formato_label.grid(row=3, column=0)
        self.formato_entry = tk.Entry(root)
        self.formato_entry.grid(row=3, column=1)
        
        self.paginas_label = tk.Label(root, text="Número de Páginas (para Livro Físico)")
        self.paginas_label.grid(row=4, column=0)
        self.paginas_entry = tk.Entry(root)
        self.paginas_entry.grid(row=4, column=1)
        
        self.adicionar_button = tk.Button(root, text="Adicionar Livro", command=self.adicionar_livro)
        self.adicionar_button.grid(row=5, column=0, columnspan=2)
        
        self.listar_button = tk.Button(root, text="Listar Livros", command=self.listar_livros)
        self.listar_button.grid(row=6, column=0, columnspan=2)
        
    def adicionar_livro(self):
        titulo = self.titulo_entry.get()
        autor = self.autor_entry.get()
        ano = self.ano_entry.get()
        formato = self.formato_entry.get()
        paginas = self.paginas_entry.get()
        
        if formato:
            livro = LivroDigital(titulo, autor, ano, formato)
        else:
            livro = LivroFisico(titulo, autor, ano, paginas)
        
        self.biblioteca.adicionar_livro(livro)
        messagebox.showinfo("Sucesso", "Livro adicionado com sucesso!")
    
    def listar_livros(self):
        livros = self.biblioteca.listar_livros()
        lista = "\n".join([f"{livro['titulo']} - {livro['autor']} ({livro['ano']})" for livro in livros])
        messagebox.showinfo("Livros", lista)

if __name__ == "__main__":
    root = tk.Tk()
    app = BibliotecaInterface(root)
    root.mainloop()
