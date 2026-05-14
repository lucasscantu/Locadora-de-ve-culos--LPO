import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import messagebox


class JanelaPrincipal(tk.Tk):
    """
    Janela Principal da aplicação (única instância de tk.Tk).
    Contém a barra de menus que dá acesso às telas secundárias (Toplevel):

        Cadastro
        ├── Veículo            -> JanelaListagemVeiculos
        └── Locações (Admin)   -> JanelaListagemLocacoes

        Ação
        └── Locar Veículo      -> JanelaLocacaoUsuario
    """

    def __init__(self):
        super().__init__()
        self.title("Locadora de Veículos - LPOO 2026/1")
        self.geometry("520x320")
        self.configure(bg="#f0f0f0")

        self._criar_menu()
        self._criar_conteudo()

    # ------------------------------------------------------------------
    # Construção dos widgets
    # ------------------------------------------------------------------
    def _criar_menu(self):
        barra_menu = tk.Menu(self)

        # ----- Menu Cadastro -----
        menu_cadastro = tk.Menu(barra_menu, tearoff=0)
        menu_cadastro.add_command(label="Veículo", command=self._abrir_listagem_veiculos)
        menu_cadastro.add_command(label="Locações (Admin)", command=self._abrir_listagem_locacoes_admin)
        barra_menu.add_cascade(label="Cadastro", menu=menu_cadastro)

        # ----- Menu Ação -----
        menu_acao = tk.Menu(barra_menu, tearoff=0)
        menu_acao.add_command(label="Locar Veículo", command=self._abrir_tela_usuario_locacao)
        barra_menu.add_cascade(label="Ação", menu=menu_acao)

        # ----- Menu Sair -----
        barra_menu.add_command(label="Sair", command=self._sair)

        self.config(menu=barra_menu)

    def _criar_conteudo(self):
        """Conteúdo simples de boas-vindas no centro da janela."""
        frame = tk.Frame(self, bg="#f0f0f0")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(
            frame,
            text="Locadora de Veículos",
            font=("Helvetica", 22, "bold"),
            bg="#f0f0f0"
        ).pack(pady=(20, 5))

        tk.Label(
            frame,
            text="Disciplina LPOO - 2026/1",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        ).pack(pady=(0, 25))

        tk.Label(
            frame,
            text=("Use a barra de menus acima para acessar:\n\n"
                  "• Cadastro → Veículo: gerenciar veículos\n"
                  "• Cadastro → Locações (Admin): CRUD completo de locações\n"
                  "• Ação → Locar Veículo: tela do usuário da locadora"),
            font=("Helvetica", 11),
            justify="left",
            bg="#f0f0f0"
        ).pack(pady=10)

    # ------------------------------------------------------------------
    # Ações dos itens de menu
    # ------------------------------------------------------------------
    def _abrir_listagem_veiculos(self):
        try:
            from view.veiculo_list_view import JanelaListagemVeiculos
            janela = JanelaListagemVeiculos(self)
            janela.transient(self)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a tela de veículos:\n{e}",
                                 parent=self)

    def _abrir_listagem_locacoes_admin(self):
        try:
            from view.locacao_list_admin_view import JanelaListagemLocacoes
            janela = JanelaListagemLocacoes(self)
            janela.transient(self)
        except Exception as e:
            messagebox.showerror("Erro",
                                 f"Não foi possível abrir a tela admin de locações:\n{e}",
                                 parent=self)

    def _abrir_tela_usuario_locacao(self):
        try:
            from view.locacao_usuario_view import JanelaLocacaoUsuario
            janela = JanelaLocacaoUsuario(self)
            janela.transient(self)
        except Exception as e:
            messagebox.showerror("Erro",
                                 f"Não foi possível abrir a tela do usuário:\n{e}",
                                 parent=self)

    def _sair(self):
        if messagebox.askyesno("Sair", "Deseja realmente encerrar a aplicação?", parent=self):
            self.destroy()
