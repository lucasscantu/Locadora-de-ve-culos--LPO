import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from model.veiculo import Categoria
from model.veiculo_factory import VeiculoFactory
from model.ExcecoesPersonalizadas import PlacaInvalidaError, TipoVeiculoInvalidoError


class VeiculoFormView(tk.Toplevel):

    def __init__(self, parent, on_salvar_callback):
        super().__init__(parent)
        self.title("Cadastrar Veiculo")
        self.resizable(False, False)
        self.grab_set()
        self.on_salvar_callback = on_salvar_callback
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        tk.Label(self, text="Placa:").grid(row=0, column=0, sticky="w", **pad)
        self.entry_placa = tk.Entry(self, width=22)
        self.entry_placa.grid(row=0, column=1, **pad)

        tk.Label(self, text="Tipo:").grid(row=1, column=0, sticky="w", **pad)
        self.combo_tipo = ttk.Combobox(self, values=["Carro", "Motorhome"], state="readonly", width=20)
        self.combo_tipo.current(0)
        self.combo_tipo.grid(row=1, column=1, **pad)

        tk.Label(self, text="Categoria:").grid(row=2, column=0, sticky="w", **pad)
        self.var_categoria = tk.StringVar(value="ECONOMICO")
        frame_cat = tk.Frame(self)
        frame_cat.grid(row=2, column=1, sticky="w", **pad)
        tk.Radiobutton(frame_cat, text="Economico", variable=self.var_categoria, value="ECONOMICO").pack(side="left")
        tk.Radiobutton(frame_cat, text="Executivo",  variable=self.var_categoria, value="EXECUTIVO").pack(side="left")

        tk.Label(self, text="Taxa Diaria (R$):").grid(row=3, column=0, sticky="w", **pad)
        self.entry_taxa = tk.Entry(self, width=22)
        self.entry_taxa.grid(row=3, column=1, **pad)

        frame_btns = tk.Frame(self)
        frame_btns.grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(frame_btns, text="Salvar",   width=10, command=self._salvar).pack(side="left", padx=6)
        tk.Button(frame_btns, text="Cancelar", width=10, command=self.destroy).pack(side="left", padx=6)

    def _salvar(self):
        placa    = self.entry_placa.get().strip()
        tipo     = self.combo_tipo.get().lower()
        taxa_str = self.entry_taxa.get().strip()
        categoria = Categoria.ECONOMICO if self.var_categoria.get() == "ECONOMICO" else Categoria.EXECUTIVO

        if not placa:
            messagebox.showwarning("Aviso", "Informe a placa.", parent=self)
            return
        if not taxa_str:
            messagebox.showwarning("Aviso", "Informe a taxa diaria.", parent=self)
            return
        try:
            taxa_diaria = float(taxa_str.replace(",", "."))
            if taxa_diaria <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Taxa diaria deve ser um numero positivo.", parent=self)
            return

        try:
            novo = VeiculoFactory.criar_veiculo(tipo, placa, taxa_diaria, categoria)
        except PlacaInvalidaError as e:
            messagebox.showerror("Placa invalida", str(e), parent=self)
            return
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self)
            return

        self.on_salvar_callback(novo)
        self.destroy()
