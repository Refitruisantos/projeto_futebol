from dados import carregar_dados
from perfil_jogador import gerar_perfis
from modelo import treinar_modelo, prever_quebras
from visualizacao import mostrar_dashboard
import argparse
import os
import pandas as pd
from datetime import datetime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--data-inicio", type=str, default=None)
    parser.add_argument("--data-fim", type=str, default=None)
    parser.add_argument("--model", type=str, default="rf")
    parser.add_argument("--save-outputs", action="store_true")
    parser.add_argument("--no-dashboard", action="store_true")
    args = parser.parse_args()

    if args.threshold is not None:
        os.environ["RISCO_PSE_THRESHOLD"] = str(args.threshold)

    try:
        dados = carregar_dados()
    except FileNotFoundError:
        print("Erro: Ficheiros 'gps.csv' ou 'pse.csv' não encontrados na pasta 'dados'.")
        return

    if args.data_inicio or args.data_fim:
        df = dados.copy()
        if args.data_inicio:
            df = df[df['data'] >= pd.to_datetime(args.data_inicio)]
        if args.data_fim:
            df = df[df['data'] <= pd.to_datetime(args.data_fim)]
        dados = df

    perfis = gerar_perfis(dados)

    modelo = treinar_modelo(perfis, model_type=args.model)

    alertas = prever_quebras(modelo, perfis)

    if args.save_outputs:
        os.makedirs("outputs", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        pd.DataFrame.from_dict(perfis, orient='index').to_csv(f"outputs/perfis_{ts}.csv")
        pd.DataFrame.from_dict(alertas, orient='index').to_csv(f"outputs/alertas_{ts}.csv")

    if not args.no_dashboard:
        mostrar_dashboard(perfis, alertas)

if __name__ == "__main__":
    main()
