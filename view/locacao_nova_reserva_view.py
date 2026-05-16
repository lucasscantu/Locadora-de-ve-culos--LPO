import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date, timedelta

from control.locacao_controller import LocacaoController
from model.veiculo import Categoria


class JanelaNovaReserva(tk.Toplevel):
    """
    Formulário do USUÁRIO para criar uma Nova Reserva.

    Aplica as validações de negócio:
      - data_inicio >= hoje;
      - data_inicio <= data_fim;
      - lista apenas veículos disponíveis no período E na categoria;
      - status sempre criado como 'reservado'.
    """

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Nova Reserva")
        self.geometry("520x480")

        self.controller = LocacaoController()
        self.veiculos_disponiveis = []  # cache da última busca

        self._criar_widgets()

        # Garante que o teclado funcione na janela recém-aberta
        self.lift()
        self.focus_force()
        self.after(100, self.txt_data_inicio.focus_set)

    # ------------------------------------------------------------------
    # Widgets
    # ------------------------------------------------------------------
    def _criar_widgets(self):
        tk.Label(self, text="Nova Reserva", font=("Helvetica", 16, "bold")).pack(pady=10)

        frm = tk.Frame(self)
        frm.pack(fill="x", padx=20, pady=5)

        # Data início
        tk.Label(frm, text="Data de início (AAAA-MM-DD):").grid(row=0, column=0, sticky="w", pady=5)
        self.txt_data_inicio = tk.Entry(frm, width=30)
        self.txt_data_inicio.grid(row=0, column=1, sticky="ew", pady=5)
        self.txt_data_inicio.insert(0, date.today().strftime("%Y-%m-%d"))

        # Data fim
        tk.Label(frm, text="Data de fim (AAAA-MM-DD):").grid(row=1, column=0, sticky="w", pady=5)
        self.txt_data_fim = tk.Entry(frm, width=30)
        self.txt_data_fim.grid(row=1, column=1, sticky="ew", pady=5)
        # Sugestão: data fim = início + 1 dia
        self.txt_data_fim.insert(0, (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"))

        # Categoria
        tk.Label(frm, text="Categoria:").grid(row=2, column=0, sticky="w", pady=5)
        self.cb_categoria = ttk.Combobox(
            frm,
            values=["(Todas)"] + [c.name for c in Categoria],
            state="readonly",
            width=28
        )
        self.cb_categoria.current(0)
        self.cb_categoria.grid(row=2, column=1, sticky="ew", pady=5)

        frm.columnconfigure(1, weight=1)

        # Botão para buscar disponíveis
        tk.Button(self, text="Buscar veículos disponíveis",
                  command=self._buscar_disponiveis).pack(pady=10)

        # Combobox de veículos disponíveis
        frm_veic = tk.Frame(self)
        frm_veic.pack(fill="x", padx=20, pady=5)
        tk.Label(frm_veic, text="Veículo disponível:").grid(row=0, column=0, sticky="w", pady=5)
        self.cb_veiculo = ttk.Combobox(frm_veic, state="readonly", width=40)
        self.cb_veiculo.grid(row=0, column=1, sticky="ew", pady=5)
        self.cb_veiculo.bind("<<ComboboxSelected>>", lambda e: self._atualizar_valor_estimado())
        frm_veic.columnconfigure(1, weight=1)

        # Label de valor estimado
        self.lbl_valor_estimado = tk.Label(self, text="", fg="#006600", font=("Helvetica", 10, "bold"))
        self.lbl_valor_estimado.pack(pady=2)

        # Aviso
        tk.Label(self,
                 text=("A lista de veículos é filtrada conforme as datas e categoria.\n"
                       "Veículos já reservados ou locados no período não aparecem."),
                 fg="#555", justify="left").pack(pady=8, padx=20)

        # Botões finais
        frm_btns = tk.Frame(self)
        frm_btns.pack(pady=15)
        tk.Button(frm_btns, text="Confirmar Reserva", width=20,
                  command=self._confirmar).pack(side="left", padx=5)
        tk.Button(frm_btns, text="Cancelar", width=12,
                  command=self.destroy).pack(side="left", padx=5)

    # ------------------------------------------------------------------
    # Lógica
    # ------------------------------------------------------------------
    def _atualizar_valor_estimado(self):
        """Exibe o valor estimado da locação ao selecionar um veículo."""
        from datetime import datetime
        from model.LocacaoStrategy import CalculoPadraoStrategy

        texto = self.cb_veiculo.get().strip()
        if not texto:
            self.lbl_valor_estimado.config(text="")
            return

        placa = texto.split(" ")[0]
        veiculo = next((v for v in self.veiculos_disponiveis if v.placa == placa), None)
        if veiculo is None:
            self.lbl_valor_estimado.config(text="")
            return

        data_inicio_str = self.txt_data_inicio.get().strip()
        data_fim_str = self.txt_data_fim.get().strip()

        try:
            data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
            data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
        except ValueError:
            self.lbl_valor_estimado.config(text="")
            return

        dias = (data_fim - data_inicio).days
        if dias <= 0:
            dias = 1

        estrategia = CalculoPadraoStrategy()
        valor = estrategia.calcular_diarias(veiculo, dias)

        self.lbl_valor_estimado.config(
            text=f"💰 Estimativa: {dias} dia(s) × R$ {veiculo.taxa_diaria:.2f} + seguro = R$ {valor:.2f}",
            fg="#006600"
        )

    def _buscar_disponiveis(self):
        data_inicio = self.txt_data_inicio.get().strip()
        data_fim = self.txt_data_fim.get().strip()
        categoria_str = self.cb_categoria.get().strip()
        if categoria_str == "(Todas)":
            categoria_str = None

        veiculos, erro = self.controller.buscar_veiculos_disponiveis(
            data_inicio, data_fim, categoria_str
        )
        if erro:
            messagebox.showerror("Erro", erro, parent=self)
            self.veiculos_disponiveis = []
            self.cb_veiculo['values'] = []
            self.cb_veiculo.set("")
            return

        self.veiculos_disponiveis = veiculos
        if not veiculos:
            messagebox.showinfo("Sem veículos",
                                "Nenhum veículo disponível nesse período/categoria.",
                                parent=self)
            self.cb_veiculo['values'] = []
            self.cb_veiculo.set("")
            return

        valores = [
            f"{v.placa} - {type(v).__name__} ({v.categoria.name}) - R$ {v.taxa_diaria:.2f}/dia"
            for v in veiculos
        ]
        self.cb_veiculo['values'] = valores
        self.cb_veiculo.current(0)
        self.update_idletasks()  # garante que o combobox registrou o valor antes do cálculo
        self._atualizar_valor_estimado()

    def _confirmar(self):
        texto = self.cb_veiculo.get().strip()
        if not texto:
            messagebox.showwarning("Aviso",
                                   "Clique em 'Buscar veículos disponíveis' e selecione um veículo.",
                                   parent=self)
            return
        placa = texto.split(" ")[0]

        data_inicio = self.txt_data_inicio.get().strip()
        data_fim = self.txt_data_fim.get().strip()

        sucesso, msg, _ = self.controller.salvar_locacao(
            placa, data_inicio, data_fim,
            status_str="reservado", modo_admin=False
        )
        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)
