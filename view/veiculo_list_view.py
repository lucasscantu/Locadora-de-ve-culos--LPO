import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

# persistencia local
# lista_veiculos = []

#from dao.veiculo_dao import VeiculoDAO
#veiculo_dao = VeiculoDAO()
#lista_veiculos = veiculo_dao.listar_todos()


from control.veiculo_controller import VeiculoController



## Toda aplicação Tkinter só deve possuir uma única janela principal raiz (tk.Tk()). 
# Se tentar dar tk.Tk() em outra tela, vai abrir outra instância na memória 
# e pode dar diversos problemas gráficos e falhas de variáveis.

# No caso do seu projeto da Locadora: As telas herdam de tk.Toplevel (class JanelaCadastroVeiculo(tk.Toplevel):) 
# porque isso permite tratá-las de um jeito modular (como um "Popup").

## O tk.Toplevel é uma classe do Tkinter usada para criar Janelas Secundárias que rodam 
# "por cima" de uma tela principal (que é geralmente o tk.Tk()).
class JanelaListagemVeiculos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Veículos Cadastrados")
        self.geometry("800x400")
        
        self.controller = VeiculoController()
        
        self.criar_widgets()
        self.carregar_dados()

    def criar_widgets(self):
        lbl_titulo = tk.Label(self, text="Veículos Cadastrados", font=("Helvetica", 16, "bold"))
        lbl_titulo.pack(pady=10)

        # Frame para a Treeview e Scrollbar
        frame_tree = tk.Frame(self)
        frame_tree.pack(expand=True, fill="both", padx=20, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")


        # Treeview (Tabela)
        colunas = ("Placa", "Tipo", "Categoria", "Taxa Diária (R$)")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", yscrollcommand=scrollbar.set)
        
        # Configurar cabeçalhos e colunas
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)

        # Frame para os botões de ação
        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=5)

        btn_novo = tk.Button(frame_botoes, text="Novo", width=10, command=self.abrir_novo)
        btn_novo.pack(side="left", padx=5)

        btn_editar = tk.Button(frame_botoes, text="Editar", width=15, command=self.abrir_editar)
        btn_editar.pack(side="left", padx=5)
        
        btn_info = tk.Button(frame_botoes, text="Ver Informações", width=15, command=self.mostrar_info)
        btn_info.pack(side="left", padx=5)

        btn_remover = tk.Button(frame_botoes, text="Remover", width=10, command=self.remover_veiculo)
        btn_remover.pack(side="left", padx=5)

        # Botão Fechar no canto direito
        btn_fechar = tk.Button(frame_botoes, text="Fechar", width=10, command=self.destroy)
        btn_fechar.pack(side="right", padx=5)

    def abrir_novo(self):
        # Vai reaproveitar a JanelaCadastroVeiculo
        from view.veiculo_view import JanelaCadastroVeiculo
        janela_cadastro = JanelaCadastroVeiculo(self)
        
        # Faz a janela de listagem "esperar" até que a janela de cadastro seja fechada
        self.wait_window(janela_cadastro)
        
        # Recarrega os dados na tabela após o cadastro ser concluído
        self.carregar_dados()

    def mostrar_info(self):
        # 1. Verifica qual linha da tabela (Treeview) está selecionada
        selecionado = self.tree.selection()
        
        # 2. Se nenhuma linha foi selecionada, exibe um aviso e cancela a ação (Return)
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um veículo para visualizar informações.", parent=self)
            return
            
        # 3. Pega os valores da linha que foi clicada. 
        # O item['values'][0] é a primeira coluna da tabela (que configuramos para ser a Placa)
        item = self.tree.item(selecionado[0])
        placa = item['values'][0]
            
        # 4. Trazemos a "lista_veiculos" global, onde todos os objetos de modelo estão salvos.
        #global lista_veiculos
        #lista_veiculos = veiculo_dao.listar_todos()
        
        
        # 5. Procura na lista o objeto exato do Veículo que tenha a mesma placa da linha clicada
        # O comando "next(...)" retorna o primeiro veículo encontrado que possui essa placa.
        #veiculo = next((v for v in lista_veiculos if v.placa == placa), None)
        
        veiculo = self.controller.buscar_por_placa(placa)
            
        # 6. Se o veículo foi encontrado na lista de persistência...
        if veiculo:
            try:
                # Chama o método exibir_dados() da classe modelo (Carro/Motorhome) que acabamos de adicionar
                info = veiculo.exibir_dados()
            except AttributeError:
                # Caso a classe do modelo não tenha o método exibir_dados() por alguma razão,
                # cria uma string básica com as informações para evitar que o código quebre
                info = f"Placa: {veiculo.placa}\nCategoria: {veiculo.categoria}\nTaxa: R$ {veiculo.taxa_diaria:.2f}"
            
            # 7. Dispara a Caixa de Diálogo do Windows/Mac (Popup) apresentando no centro da tela as informações obtidas
            messagebox.showinfo("Informações do Veículo", info, parent=self)
        else:
            # 8. Só vai cair aqui se por algum motivo houver erro de inconsistência 
            # (ex: Constava na tabela mas foi excluído do código/banco localmente).
            messagebox.showerror("Erro", "Veículo não encontrado.", parent=self)


    def remover_veiculo(self):
        # 1. Verifica qual linha da tabela (Treeview) está selecionada
        selecionado = self.tree.selection()
        
        # 2. Se nenhuma linha foi selecionada, exibe um aviso e cancela a ação (Return)
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um veículo para remover.", parent=self)
            return

        # 3. Pega os valores da linha que foi clicada, com informação da placa - 1º dado da linha
        item = self.tree.item(selecionado[0])
        placa = item['values'][0]
        
        # 4. Verifica se o usuário quer remover o objeto
        resposta = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja remover o veículo de placa {placa}?", parent=self)
        if resposta:
            # 5. Chama o controller para remover do banco de dados
            sucesso, msg = self.controller.remover_veiculo(placa)
            
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=self)
                # 6. Recarregar as informações na tabela
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", msg, parent=self)

    def carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        veiculos = self.controller.listar_veiculos()
        
        if veiculos is None:
             messagebox.showerror("Erro", "Erro ao carregar veículos.", parent=self)
             return
             
        for v in veiculos:
            tipo_nome = type(v).__name__
            taxa_formatada = f"R$ {v.taxa_diaria:.2f}".replace('.', ',')
            categoria_texto = v.categoria.name if hasattr(v.categoria, 'name') else str(v.categoria)
            
            self.tree.insert("", "end", values=(
                v.placa, 
                tipo_nome, 
                categoria_texto, 
                taxa_formatada
            ))

    def abrir_editar(self):
        # 1. Verifica qual linha da tabela (Treeview) está selecionada
        selecionado = self.tree.selection()
        
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um veículo para editar.", parent=self)
            return

        # 2. Pega a placa do veículo
        item = self.tree.item(selecionado[0])
        placa = item['values'][0]

        # 3. Busca o veículo via Controller
        veiculo = self.controller.buscar_por_placa(placa)
        if not veiculo:
            messagebox.showerror("Erro", "Veículo não encontrado.", parent=self)
            return

        # 4. Abre a janela de cadastro, mas em modo de edição (passando o veículo)
        from view.veiculo_view import JanelaCadastroVeiculo
        janela_edicao = JanelaCadastroVeiculo(self, veiculo_existente=veiculo)
        
        self.wait_window(janela_edicao)
        
        # 5. Recarrega a tabela após a edição
        self.carregar_dados()