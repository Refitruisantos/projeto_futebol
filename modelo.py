import numpy as np
from sklearn.ensemble import RandomForestClassifier

def treinar_modelo(perfis):
    X = []
    y = []

    # Certifique-se de que há dados para treinar
    if not perfis:
        # Retorna um modelo não treinado ou lida com o erro
        return RandomForestClassifier() 

    for jogador, perfil in perfis.items():
        # Lida com possíveis valores NaN
        if any(np.isnan(val) for val in [perfil['media_distancia'], perfil['velocidade_max'], perfil['pse_medio']]):
            continue
        X.append([perfil['media_distancia'], perfil['velocidade_max'], perfil['pse_medio']])
        y.append(1 if perfil['pse_medio'] > 7 else 0)  # Exemplo: risco alto se PSE > 7

    # Verifica se há amostras suficientes para treinar
    if not X:
        return RandomForestClassifier()

    modelo = RandomForestClassifier(random_state=42)
    modelo.fit(X, y)
    return modelo

def prever_quebras(modelo, perfis):
    alertas = {}

    for jogador, perfil in perfis.items():
        # Lida com possíveis valores NaN
        if any(np.isnan(val) for val in [perfil['media_distancia'], perfil['velocidade_max'], perfil['pse_medio']]):
            alertas[jogador] = -1 # -1 pode indicar dados insuficientes
            continue

        entrada = np.array([[perfil['media_distancia'], perfil['velocidade_max'], perfil['pse_medio']]])
        
        # Verifica se o modelo foi treinado
        if not hasattr(modelo, "classes_"):
            alertas[jogador] = -1 # Modelo não treinado
            continue

        risco = modelo.predict(entrada)[0]
        alertas[jogador] = risco

    return alertas
