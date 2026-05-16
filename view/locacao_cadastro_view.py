import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date

from control.locacao_controller import LocacaoController
from model.veiculo import Categoria
from model.locacao import StatusLocacao


class JanelaCadastroLocacao(tk.Toplevel):
    """
    Formulário do Administrador para criar ou editar uma locação.

    No modo Administrador todos os campos são editáveis, inclusive o status.
    A única regra básica validada é: data_inicio <= data_fim.
    """

    def __init__(self, master=None, locacao_existente=None):
        super().__init__(master)
        self.locacao_existente = locacao_existente
        self.controller = LocacaoController()

        self.title("Editar Locação" if locacao_existente else "Nova Locação (Admin)")
        self.geometry("500x460")

        self._criar_widgets()

        if locacao_existente:
            self._preencher_dados()
        else:
            # Em criação, atualiza dropdown com todos os veículos (admin pode usar qualquer um)
            self._atualizar_lista_veiculos()

        # Garante que o teclado funcione na janela recém-aberta
        self.lift()
        self.focus_force()
        self.after(100, self.txt_data_inicio.focus_set)

        # Vincula eventos para recalcular valor automaticamente
        self.txt_data_inicio.bind("<FocusOut>", lambda e: self._calcular_valor_automatico())
        self.txt_data_inicio.bind("<KeyRelease>", lambda e: self._calcular_valor_automatico())
        self.txt_data_fim.bind("<FocusOut>", lambda e: self._calcular_valor_automatico())
        self.txt_data_fim.bind("<KeyRelease>", lambda e: self._calcular_valor_automatico())
        self.cb_veiculo.bind("<<ComboboxSelected>>", lambda e: self._calcular_valor_automatico())

    # ------------------------------------------------------------------
    # Widgets
    # ------------------------------------------------------------------
    def _criar_widgets(self):
        titulo = "Editar Locação" if self.locacao_existente else "Nova Locação (Admin)"
        tk.Label(self, text=titulo, font=("Helvetica", 16, "bold")).pack(pady=10)

        # Frame de campos
        frm = tk.Frame(self)
        frm.pack(fill="x", padx=20, pady=5)

        # Veículo (placa - usaremos um combobox com todos os veículos)
        tk.Label(frm, text="Veículo (placa):").grid(row=0, column=0, sticky="w", pady=5)
        self.cb_veiculo = ttk.Combobox(frm, state="readonly", width=35)
        self.cb_veiculo.grid(row=0, column=1, sticky="ew", pady=5)

        # Data de início
        tk.Label(frm, text="Data de início (AAAA-MM-DD):").grid(row=1, column=0, sticky="w", pady=5)
        self.txt_data_inicio = tk.Entry(frm, width=37)
        self.txt_data_inicio.grid(row=1, column=1, sticky="ew", pady=5)
        self.txt_data_inicio.insert(0, date.today().strftime("%Y-%m-%d"))

        # Data de fim
        tk.Label(frm, text="Data de fim (AAAA-MM-DD):").grid(row=2, column=0, sticky="w", pady=5)
        self.txt_data_fim = tk.Entry(frm, width=37)
        self.txt_data_fim.grid(row=2, column=1, sticky="ew", pady=5)

        # Status
        tk.Label(frm, text="Status:").grid(row=3, column=0, sticky="w", pady=5)
        self.cb_status = ttk.Combobox(
            frm,
            values=[s.value for s in StatusLocacao],
            state="readonly",
            width=35
        )
        self.cb_status.set(StatusLocacao.RESERVADO.value)
        self.cb_status.grid(row=3, column=1, sticky="ew", pady=5)

        # Valor total
        tk.Label(frm, text="Valor total (R$):").grid(row=4, column=0, sticky="w", pady=5)
        self.txt_valor = tk.Entry(frm, width=37)
        self.txt_valor.grid(row=4, column=1, sticky="ew", pady=5)

        # Label de feedback do cálculo automático
        self.lbl_calculo = tk.Label(frm, text="", fg="#006600", font=("Helvetica", 9))
        self.lbl_calculo.grid(row=5, column=1, sticky="w")

        frm.columnconfigure(1, weight=1)

        # Aviso para o admin
        tk.Label(self,
                 text=("Modo Administrador: regras de disponibilidade NÃO são aplicadas.\n"
                       "A única validação obrigatória é data de início ≤ data de fim."),
                 fg="#aa6600", justify="left").pack(pady=8, padx=20)

        # Botões
        frm_botoes = tk.Frame(self)
        frm_botoes.pack(pady=15)
        texto_botao = "Atualizar Locação" if self.locacao_existente else "Salvar Locação"
        tk.Button(frm_botoes, text=texto_botao, command=self._salvar, width=20).pack(side="left", padx=5)
        tk.Button(frm_botoes, text="Cancelar", command=self.destroy, width=12).pack(side="left", padx=5)

    # ------------------------------------------------------------------
    # Lógica
    # ------------------------------------------------------------------
    def _calcular_valor_automatico(self):
        """Calcula o valor total automaticamente com base na taxa diária e nas datas."""
        from datetime import datetime
        from model.LocacaoStrategy import CalculoPadraoStrategy

        placa = self._placa_selecionada()
        data_inicio_str = self.txt_data_inicio.get().strip()
        data_fim_str = self.txt_data_fim.get().strip()

        if not placa or not data_inicio_str or not data_fim_str:
            self.lbl_calculo.config(text="")
            return

        try:
            data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
            data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
        except ValueError:
            self.lbl_calculo.config(text="")
            return

        if data_inicio > data_fim:
            self.lbl_calculo.config(text="⚠ Data início > data fim", fg="#cc0000")
            return

        dias = (data_fim - data_inicio).days
        if dias <= 0:
            dias = 1

        # Busca o veículo pelo placa para obter a taxa diária
        veiculos = self.controller.veiculo_dao.listar_todos()
        veiculo = next((v for v in veiculos if v.placa == placa), None)
        if veiculo is None:
            self.lbl_calculo.config(text="")
            return

        estrategia = CalculoPadraoStrategy()
        valor = estrategia.calcular_diarias(veiculo, dias)

        # Preenche o campo de valor automaticamente
        self.txt_valor.delete(0, tk.END)
        self.txt_valor.insert(0, f"{valor:.2f}")
        self.lbl_calculo.config(
            text=f"✔ {dias} dia(s) × R$ {veiculo.taxa_diaria:.2f} + seguro = R$ {valor:.2f}",
            fg="#006600"
        )

    def _atualizar_lista_veiculos(self):
        """Carrega TODOS os veículos no combobox (admin tem acesso irrestrito)."""
        veiculos = self.controller.veiculo_dao.listar_todos()
        valores = [f"{v.placa} ({type(v).__name__} - {v.categoria.name})" for v in veiculos]
        self.cb_veiculo['values'] = valores
        if valores:
            self.cb_veiculo.current(0)

    def _placa_selecionada(self):
        """Extrai apenas a placa do texto exibido no combobox."""
        texto = self.cb_veiculo.get().strip()
        if not texto:
            return None
        return texto.split(" ")[0]

    def _preencher_dados(self):
        loc = self.locacao_existente
        # Carrega lista de veículos para o combobox
        veiculos = self.controller.veiculo_dao.listar_todos()
        valores = [f"{v.placa} ({type(v).__name__} - {v.categoria.name})" for v in veiculos]
        self.cb_veiculo['values'] = valores
        # Procura o item correspondente ao veículo atual
        placa_atual = loc.veiculo.placa
        for i, val in enumerate(valores):
            if val.startswith(placa_atual + " "):
                self.cb_veiculo.current(i)
                break

        self.txt_data_inicio.delete(0, tk.END)
        self.txt_data_inicio.insert(0, loc.data_inicio.strftime("%Y-%m-%d"))

        if loc.data_fim:
            self.txt_data_fim.delete(0, tk.END)
            self.txt_data_fim.insert(0, loc.data_fim.strftime("%Y-%m-%d"))

        self.cb_status.set(loc.status.value)

        if loc.valor_total is not None:
            self.txt_valor.delete(0, tk.END)
            self.txt_valor.insert(0, f"{loc.valor_total:.2f}")

    def _salvar(self):
        placa = self._placa_selecionada()
        data_inicio = self.txt_data_inicio.get().strip()
        data_fim = self.txt_data_fim.get().strip()
        status = self.cb_status.get().strip()
        valor = self.txt_valor.get().strip()

        if self.locacao_existente:
            sucesso, msg = self.controller.atualizar_locacao(
                self.locacao_existente.id, placa, data_inicio, data_fim, status, valor
            )
        else:
            sucesso, msg, _ = self.controller.salvar_locacao(
                placa, data_inicio, data_fim, status,
                valor_total=valor if valor else None, modo_admin=True
            )

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)
