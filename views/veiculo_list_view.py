import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from model.veiculo import Categoria
from model.veiculo_factory import VeiculoFactory
from views.veiculo_form_view import VeiculoFormView


class VeiculoListView(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Locadora de Veiculos")
        self.geometry("660x380")
        self._veiculos = []
        self._build_ui()
        self._popular_exemplos()

    def _build_ui(self):
        tk.Label(self, text="Veiculos Cadastrados", font=("Arial", 12, "bold")).pack(pady=(10, 4))

        frame_tabela = tk.Frame(self)
        frame_tabela.pack(fill="both", expand=True, padx=10)

        colunas = ("placa", "tipo", "categoria", "taxa_diaria", "seguro")
        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings")

        self.tree.heading("placa",      text="Placa")
        self.tree.heading("tipo",       text="Tipo")
        self.tree.heading("categoria",  text="Categoria")
        self.tree.heading("taxa_diaria",text="Taxa Diaria")
        self.tree.heading("seguro",     text="Seguro")

        self.tree.column("placa",       width=100, anchor="center")
        self.tree.column("tipo",        width=100, anchor="center")
        self.tree.column("categoria",   width=110, anchor="center")
        self.tree.column("taxa_diaria", width=110, anchor="center")
        self.tree.column("seguro",      width=90,  anchor="center")

        scroll = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        frame_botoes = tk.Frame(self)
        frame_botoes.pack(pady=10)

        tk.Button(frame_botoes, text="Novo",            width=14, command=self._abrir_formulario).pack(side="left", padx=6)
        tk.Button(frame_botoes, text="Ver Informacoes", width=14, command=self._ver_informacoes).pack(side="left", padx=6)
        tk.Button(frame_botoes, text="Remover",         width=14, command=self._remover).pack(side="left", padx=6)

    def _popular_exemplos(self):
        dados = [
            ("carro",     "ABC1234", 150.0, Categoria.ECONOMICO),
            ("motorhome", "XYZ9A99", 300.0, Categoria.EXECUTIVO),
        ]
        for tipo, placa, taxa, cat in dados:
            try:
                v = VeiculoFactory.criar_veiculo(tipo, placa, taxa, cat)
                self._veiculos.append(v)
            except Exception:
                pass
        self._atualizar_tabela()

    def _atualizar_tabela(self):
        self.tree.delete(*self.tree.get_children())
        for i, v in enumerate(self._veiculos):
            self.tree.insert("", "end", iid=str(i), values=(
                v.placa,
                type(v).__name__,
                v.categoria.value,
                f"R$ {v.taxa_diaria:.2f}",
                f"R$ {v.valor_seguro:.2f}",
            ))

    def _get_selecionado(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um veiculo na lista.")
            return None
        return self._veiculos[int(sel)]

    def _ver_informacoes(self):
        v = self._get_selecionado()
        if v:
            messagebox.showinfo("Informacoes do Veiculo", v.exibir_dados())

    def _remover(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um veiculo para remover.")
            return
        v = self._veiculos[int(sel)]
        if messagebox.askyesno("Confirmar", f"Remover veiculo {v.placa}?"):
            self._veiculos.pop(int(sel))
            self._atualizar_tabela()

    def _abrir_formulario(self):
        VeiculoFormView(self, self._on_novo_veiculo)

    def _on_novo_veiculo(self, veiculo):
        self._veiculos.append(veiculo)
        self._atualizar_tabela()


if __name__ == "__main__":
    app = VeiculoListView()
    app.mainloop()
