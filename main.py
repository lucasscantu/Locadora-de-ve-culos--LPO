import sys
import os

# Adiciona o diretório raiz ao sys.path para garantir que os módulos sejam encontrados
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from view.janela_principal import JanelaPrincipal


if __name__ == "__main__":
    # A janela principal (tk.Tk) agora carrega a barra de menus que dá acesso
    # às demais telas (Cadastro de Veículos, CRUD admin de Locações e a tela
    # operacional do usuário da locadora).
    app = JanelaPrincipal()
    app.mainloop()
