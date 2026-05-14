import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import messagebox, ttk
from model.veiculo import VeiculoFactory, Categoria
import view.veiculo_list_view as list_view
from control.veiculo_controller import VeiculoController


class JanelaCadastroVeiculo(tk.Toplevel):
    """
    Janela de cadastro/edição de veículo.

    Notas sobre foco:
      - Quando um Toplevel é aberto a partir de outro Toplevel (no nosso caso
        JanelaPrincipal -> JanelaListagemVeiculos -> JanelaCadastroVeiculo),
        em alguns SOs/versões do Tk a nova janela ABRE mas não recebe o foco
        de teclado automaticamente, fazendo parecer que os Entry estão
        "travados" mesmo aceitando clique.
      - A solução é forçar a janela à frente (self.lift / self.focus_force)
        e agendar o focus_set do primeiro Entry com self.after(...) — assim
        o foco é dado APÓS o Tk terminar de desenhar a janela.
    """

    # Opções fixas exibidas no combobox de tipo de veículo.
    # Os valores correspondem exatamente aos tipos aceitos pelo VeiculoFactory.
    TIPOS_VEICULO = ["Carro", "Motorhome"]

    def __init__(self, master=None, veiculo_existente=None):
        super().__init__(master)

        self.veiculo_existente = veiculo_existente
        self.title("Atualizar Veículo" if veiculo_existente else "Cadastro de Novo Veículo")
        self.geometry("440x360")
        self.resizable(False, False)
        self.controller = VeiculoController()

        # ----------------------------------------------------------------
        # Título
        # ----------------------------------------------------------------
        texto_titulo = "Atualizar Veículo" if veiculo_existente else "Cadastrar Veículo"
        tk.Label(self, text=texto_titulo,
                 font=("Helvetica", 16, "bold")).pack(pady=(15, 10))

        # ----------------------------------------------------------------
        # Formulário (grid é mais previsível que pack para forms)
        # ----------------------------------------------------------------
        frm = tk.Frame(self)
        frm.pack(padx=25, pady=5, fill="x")
        frm.columnconfigure(1, weight=1)

        # Placa
        tk.Label(frm, text="Placa:").grid(row=0, column=0, sticky="w", pady=6)
        self.txt_placa = tk.Entry(frm, state="normal", takefocus=True)
        self.txt_placa.grid(row=0, column=1, sticky="ew", pady=6, padx=(10, 0))

        # Tipo (combobox readonly — usuário só escolhe Carro ou Motorhome)
        tk.Label(frm, text="Tipo:").grid(row=1, column=0, sticky="w", pady=6)
        self.cb_tipo = ttk.Combobox(frm, values=self.TIPOS_VEICULO, state="readonly")
        self.cb_tipo.current(0)
        self.cb_tipo.grid(row=1, column=1, sticky="ew", pady=6, padx=(10, 0))

        # Categoria
        tk.Label(frm, text="Categoria:").grid(row=2, column=0, sticky="w", pady=6)
        self.cb_categoria = ttk.Combobox(
            frm, values=["ECONOMICO", "EXECUTIVO", "LUXO"], state="readonly"
        )
        self.cb_categoria.current(0)
        self.cb_categoria.grid(row=2, column=1, sticky="ew", pady=6, padx=(10, 0))

        # Taxa Diária
        tk.Label(frm, text="Taxa Diária (R$):").grid(row=3, column=0, sticky="w", pady=6)
        self.txt_taxa = tk.Entry(frm, state="normal", takefocus=True)
        self.txt_taxa.grid(row=3, column=1, sticky="ew", pady=6, padx=(10, 0))

        # ----------------------------------------------------------------
        # Botão Salvar / Atualizar
        # ----------------------------------------------------------------
        texto_botao = "Atualizar Veículo" if veiculo_existente else "Salvar Veículo"
        tk.Button(self, text=texto_botao,
                  command=self.solicitar_cadastro).pack(pady=20)

        # ----------------------------------------------------------------
        # Pré-preenchimento em modo edição
        # ----------------------------------------------------------------
        if self.veiculo_existente:
            self.txt_placa.insert(0, self.veiculo_existente.placa)
            self.txt_placa.config(state="disabled")  # placa não pode mudar

            tipo_objeto = self.veiculo_existente.__class__.__name__
            if tipo_objeto in self.TIPOS_VEICULO:
                self.cb_tipo.set(tipo_objeto)
            self.cb_tipo.config(state="disabled")    # tipo também fixo em edição

            cat = self.veiculo_existente.categoria
            self.cb_categoria.set(cat.name if hasattr(cat, "name") else str(cat))
            self.txt_taxa.insert(0, f"{self.veiculo_existente.taxa_diaria}")
            campo_inicial = self.txt_taxa
        else:
            campo_inicial = self.txt_placa

        # ----------------------------------------------------------------
        # Garantia de foco/teclado funcionando
        # ----------------------------------------------------------------
        # 1) Traz a janela para a frente
        self.lift()
        # 2) Força esta Toplevel a receber o foco do sistema operacional
        self.focus_force()
        # 3) Agenda o focus_set do Entry para DEPOIS do Tk terminar de desenhar
        #    a janela (caso contrário o focus_set pode ser ignorado em alguns SOs).
        self.after(100, campo_inicial.focus_set)

    def solicitar_cadastro(self):
        placa = self.txt_placa.get().strip().upper()
        tipo = self.cb_tipo.get().strip()
        categoria = self.cb_categoria.get().strip()
        taxa_str = self.txt_taxa.get().strip()

        if not tipo:
            messagebox.showerror("Erro", "Selecione o tipo do veículo.", parent=self)
            return

        if self.veiculo_existente:
            sucesso, msg = self.controller.atualizar_veiculo(placa, tipo, categoria, taxa_str)
        else:
            sucesso, msg = self.controller.salvar_veiculo(placa, tipo, categoria, taxa_str)

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
        else:
            messagebox.showerror("Erro", msg, parent=self)

        self.destroy()
