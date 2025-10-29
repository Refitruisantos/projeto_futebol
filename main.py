from dados import carregar_dados
from perfil_jogador import gerar_perfis
from modelo import treinar_modelo, prever_quebras
from visualizacao import mostrar_dashboard

def main():
    # 1. Carregar dados GPS + PSE
    # Certifique-se de que os ficheiros gps.csv e pse.csv existem na pasta 'dados'
    try:
        dados = carregar_dados()
    except FileNotFoundError:
        print("Erro: Ficheiros 'gps.csv' ou 'pse.csv' não encontrados na pasta 'dados'.")
        print("Por favor, crie-os com os dados necessários antes de executar o programa.")
        return

    # 2. Gerar perfis físicos e táticos
    perfis = gerar_perfis(dados)

    # 3. Treinar modelo preditivo
    modelo = treinar_modelo(perfis)

    # 4. Prever quedas de rendimento
    alertas = prever_quebras(modelo, perfis)

    # 5. Visualizar resultados
    mostrar_dashboard(perfis, alertas)

if __name__ == "__main__":
    main()
