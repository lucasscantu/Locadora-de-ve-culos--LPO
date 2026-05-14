import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from control.locacao_controller import LocacaoController
from model.locacao import StatusLocacao


class JanelaLocacaoUsuario(tk.Toplevel):
    """
    Tela do Usuário da Locadora.

    Mostra a listagem de locações e oferece ações operacionais:
        - Nova Reserva  (sempre habilitada)
        - Ver Detalhes  (sempre habilitada)
        - Locar         (somente se status == 'reservado')
        - Devolver      (somente se status == 'locado')
        - Cancelar      (somente se status == 'reservado')

    Os botões condicionais são habilitados/desabilitados conforme a seleção
    da TreeView é alterada.
    """

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Locar Veículo - Tela do Usuário")
        self.geometry("960x460")

        self.controller = LocacaoController()

        self._criar_widgets()
        self.carregar_dados()
        self._atualizar_estado_botoes()

    # ------------------------------------------------------------------
    # Widgets
    # ------------------------------------------------------------------
    def _criar_widgets(self):
        tk.Label(self, text="Locações - Tela do Usuário",
                 font=("Helvetica", 16, "bold")).pack(pady=10)

        frame_tree = tk.Frame(self)
        frame_tree.pack(expand=True, fill="both", padx=20, pady=10)

        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        colunas = ("ID", "Placa", "Categoria", "Início", "Fim", "Status", "Valor (R$)")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings",
                                 yscrollcommand=scrollbar.set)
        for col in colunas:
            self.tree.heading(col, text=col)
            largura = 70 if col == "ID" else 120
            self.tree.column(col, anchor="center", width=largura)
        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)

        # Quando a seleção muda, atualiza estado dos botões
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._atualizar_estado_botoes())

        # Frame de botões
        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=10)

        self.btn_nova_reserva = tk.Button(frame_botoes, text="Nova Reserva", width=14,
                                          command=self._nova_reserva)
        self.btn_nova_reserva.pack(side="left", padx=5)

        self.btn_detalhes = tk.Button(frame_botoes, text="Ver Detalhes", width=14,
                                      command=self._ver_detalhes)
        self.btn_detalhes.pack(side="left", padx=5)

        self.btn_locar = tk.Button(frame_botoes, text="Locar", width=10,
                                   command=self._locar)
        self.btn_locar.pack(side="left", padx=5)

        self.btn_devolver = tk.Button(frame_botoes, text="Devolver", width=10,
                                      command=self._devolver)
        self.btn_devolver.pack(side="left", padx=5)

        self.btn_cancelar = tk.Button(frame_botoes, text="Cancelar", width=10,
                                      command=self._cancelar)
        self.btn_cancelar.pack(side="left", padx=5)

        tk.Button(frame_botoes, text="Fechar", width=10,
                  command=self.destroy).pack(side="right", padx=5)

    # ------------------------------------------------------------------
    # Dados
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
        self._atualizar_estado_botoes()

    # ------------------------------------------------------------------
    # Estado dos botões em função da seleção
    # ------------------------------------------------------------------
    def _status_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            return None, None
        valores = self.tree.item(sel[0])['values']
        return valores[0], valores[5].lower()  # id, status

    def _atualizar_estado_botoes(self):
        id_loc, status = self._status_selecionado()

        # Nova Reserva e Ver Detalhes sempre habilitados (Ver Detalhes só faz sentido com seleção)
        self.btn_nova_reserva.config(state="normal")
        self.btn_detalhes.config(state="normal" if id_loc is not None else "disabled")

        # Locar: só com status reservado
        self.btn_locar.config(state="normal" if status == "reservado" else "disabled")
        # Devolver: só com status locado
        self.btn_devolver.config(state="normal" if status == "locado" else "disabled")
        # Cancelar: só com status reservado
        self.btn_cancelar.config(state="normal" if status == "reservado" else "disabled")

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------
    def _nova_reserva(self):
        from view.locacao_nova_reserva_view import JanelaNovaReserva
        janela = JanelaNovaReserva(self)
        self.wait_window(janela)
        self.carregar_dados()

    def _ver_detalhes(self):
        id_loc, _ = self._status_selecionado()
        if id_loc is None:
            messagebox.showwarning("Aviso",
                                   "Selecione uma locação para ver detalhes.",
                                   parent=self)
            return
        loc = self.controller.buscar_por_id(id_loc)
        if not loc:
            messagebox.showerror("Erro", "Locação não encontrada.", parent=self)
            return

        veic = loc.veiculo
        cabecalho = (f"ID: {loc.id}\n"
                     f"Veículo: {veic.placa} - {type(veic).__name__} "
                     f"({veic.categoria.name})\n"
                     f"Taxa diária: R$ {veic.taxa_diaria:.2f}\n")

        if loc.status == StatusLocacao.DEVOLVIDO:
            info = (cabecalho +
                    f"Status: Devolvida\n"
                    f"Data de início: {loc.data_inicio.strftime('%d/%m/%Y')}\n"
                    f"Data de devolução: "
                    f"{loc.data_fim.strftime('%d/%m/%Y') if loc.data_fim else '-'}\n"
                    f"Número de diárias: {loc.numero_diarias()}\n"
                    f"Valor total: R$ {loc.valor_total:.2f}"
                    if loc.valor_total is not None
                    else cabecalho + "Status: Devolvida\nValor total: -")
        elif loc.status in (StatusLocacao.RESERVADO, StatusLocacao.LOCADO):
            try:
                valor_estimado = loc.calcular_valor_locacao()
                valor_str = f"R$ {valor_estimado:.2f}"
            except Exception:
                valor_str = "(não foi possível estimar)"
            info = (cabecalho +
                    f"Status: {loc.status.value.capitalize()}\n"
                    f"Data de início: {loc.data_inicio.strftime('%d/%m/%Y')}\n"
                    f"Data de fim prevista: "
                    f"{loc.data_fim.strftime('%d/%m/%Y') if loc.data_fim else '(não definida)'}\n"
                    f"Valor estimado: {valor_str}")
        elif loc.status == StatusLocacao.CANCELADO:
            info = (cabecalho +
                    f"Status: Cancelada\n"
                    f"Data de início: {loc.data_inicio.strftime('%d/%m/%Y')}\n"
                    f"Data de fim: "
                    f"{loc.data_fim.strftime('%d/%m/%Y') if loc.data_fim else '-'}\n"
                    f"Esta locação foi cancelada antes da retirada do veículo.")
        else:
            info = cabecalho + f"Status: {loc.status.value}"

        messagebox.showinfo("Detalhes da Locação", info, parent=self)

    def _locar(self):
        id_loc, _ = self._status_selecionado()
        if id_loc is None:
            return
        sucesso, msg, locacao = self.controller.locar(id_loc)
        if sucesso:
            messagebox.showinfo("Sucesso",
                                f"{msg}\nData de retirada registrada: "
                                f"{locacao.data_inicio.strftime('%d/%m/%Y')}",
                                parent=self)
            self.carregar_dados()
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def _devolver(self):
        id_loc, _ = self._status_selecionado()
        if id_loc is None:
            return
        if not messagebox.askyesno("Confirmar Devolução",
                                   f"Confirmar a devolução da locação ID {id_loc}?",
                                   parent=self):
            return
        sucesso, msg, info = self.controller.devolver(id_loc)
        if sucesso:
            texto = (f"{msg}\n\n"
                     f"Data de início: {info['data_inicio'].strftime('%d/%m/%Y')}\n"
                     f"Data de devolução: {info['data_devolucao'].strftime('%d/%m/%Y')}\n"
                     f"Número de diárias: {info['numero_diarias']}\n"
                     f"Valor total da locação: R$ {info['valor_total']:.2f}")
            messagebox.showinfo("Devolução Registrada", texto, parent=self)
            self.carregar_dados()
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def _cancelar(self):
        id_loc, _ = self._status_selecionado()
        if id_loc is None:
            return
        if not messagebox.askyesno("Confirmar Cancelamento",
                                   f"Confirmar o cancelamento da locação ID {id_loc}?",
                                   parent=self):
            return
        sucesso, msg = self.controller.cancelar(id_loc)
        if sucesso:
            messagebox.showinfo("Sucesso", "Locação cancelada com sucesso.", parent=self)
            self.carregar_dados()
        else:
            messagebox.showerror("Erro", msg, parent=self)
