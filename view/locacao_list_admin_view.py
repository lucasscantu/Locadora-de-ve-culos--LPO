import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from control.locacao_controller import LocacaoController


class JanelaListagemLocacoes(tk.Toplevel):
    """
    Tela do Administrador - CRUD completo de locações.

    O Administrador pode adicionar, editar, visualizar e remover locações
    sem as restrições aplicadas à tela do usuário.
    """

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Locações - Administração")
        self.geometry("960x440")

        self.controller = LocacaoController()

        self._criar_widgets()
        self.carregar_dados()

    # ------------------------------------------------------------------
    # Widgets
    # ------------------------------------------------------------------
    def _criar_widgets(self):
        tk.Label(self, text="Locações Cadastradas (Admin)",
                 font=("Helvetica", 16, "bold")).pack(pady=10)

        frame_tree = tk.Frame(self)
        frame_tree.pack(expand=True, fill="both", padx=20, pady=10)

        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        colunas = ("ID", "Placa", "Categoria", "Início", "Fim", "Status", "Valor Total (R$)")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings",
                                 yscrollcommand=scrollbar.set)

        for col in colunas:
            self.tree.heading(col, text=col)
            largura = 80 if col == "ID" else 120
            self.tree.column(col, anchor="center", width=largura)

        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)

        # Botões
        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=5)

        tk.Button(frame_botoes, text="Adicionar", width=12,
                  command=self._adicionar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Editar", width=12,
                  command=self._editar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Visualizar", width=12,
                  command=self._visualizar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Remover", width=12,
                  command=self._remover).pack(side="left", padx=5)

        tk.Button(frame_botoes, text="Fechar", width=10,
                  command=self.destroy).pack(side="right", padx=5)

    # ------------------------------------------------------------------
    # Operações
    # ------------------------------------------------------------------
    def carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        locacoes = self.controller.listar_locacoes()
        for l in locacoes:
            data_fim = l.data_fim.strftime("%d/%m/%Y") if l.data_fim else "-"
            valor = f"{l.valor_total:.2f}".replace('.', ',') if l.valor_total else "-"
            categoria = l.veiculo.categoria.name if hasattr(l.veiculo.categoria, 'name') \
                else str(l.veiculo.categoria)
            self.tree.insert("", "end", values=(
                l.id,
                l.veiculo.placa,
                categoria,
                l.data_inicio.strftime("%d/%m/%Y"),
                data_fim,
                l.status.value.capitalize(),
                valor
            ))

    def _id_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])['values'][0]

    def _adicionar(self):
        from view.locacao_cadastro_view import JanelaCadastroLocacao
        janela = JanelaCadastroLocacao(self)
        self.wait_window(janela)
        self.carregar_dados()

    def _editar(self):
        id_loc = self._id_selecionado()
        if id_loc is None:
            messagebox.showwarning("Aviso",
                                   "Selecione uma locação para editar.",
                                   parent=self)
            return
        locacao = self.controller.buscar_por_id(id_loc)
        if not locacao:
            messagebox.showerror("Erro", "Locação não encontrada.", parent=self)
            return
        from view.locacao_cadastro_view import JanelaCadastroLocacao
        janela = JanelaCadastroLocacao(self, locacao_existente=locacao)
        self.wait_window(janela)
        self.carregar_dados()

    def _visualizar(self):
        id_loc = self._id_selecionado()
        if id_loc is None:
            messagebox.showwarning("Aviso",
                                   "Selecione uma locação para visualizar.",
                                   parent=self)
            return
        locacao = self.controller.buscar_por_id(id_loc)
        if not locacao:
            messagebox.showerror("Erro", "Locação não encontrada.", parent=self)
            return

        data_fim = locacao.data_fim.strftime("%d/%m/%Y") if locacao.data_fim else "(não definida)"
        valor = (f"R$ {locacao.valor_total:.2f}".replace('.', ',')
                 if locacao.valor_total is not None else "(não calculado)")

        info = (f"ID: {locacao.id}\n"
                f"Veículo: {locacao.veiculo.placa} "
                f"({type(locacao.veiculo).__name__} - {locacao.veiculo.categoria.name})\n"
                f"Taxa diária: R$ {locacao.veiculo.taxa_diaria:.2f}\n"
                f"Data de início: {locacao.data_inicio.strftime('%d/%m/%Y')}\n"
                f"Data de fim: {data_fim}\n"
                f"Status: {locacao.status.value.capitalize()}\n"
                f"Valor total: {valor}")

        messagebox.showinfo("Detalhes da Locação", info, parent=self)

    def _remover(self):
        id_loc = self._id_selecionado()
        if id_loc is None:
            messagebox.showwarning("Aviso",
                                   "Selecione uma locação para remover.",
                                   parent=self)
            return
        if not messagebox.askyesno("Confirmar Exclusão",
                                   f"Tem certeza que deseja remover a locação ID {id_loc}?",
                                   parent=self):
            return
        sucesso, msg = self.controller.remover_locacao(id_loc)
        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.carregar_dados()
        else:
            messagebox.showerror("Erro", msg, parent=self)
