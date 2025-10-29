def gerar_perfis(dados):
    perfis = {}

    for jogador in dados['jogador_id'].unique():
        sub = dados[dados['jogador_id'] == jogador]
        perfil = {
            'media_distancia': sub['distancia_total'].mean(),
            'velocidade_max': sub['velocidade_max'].max(),
            'pse_medio': sub['pse'].mean(),
            'sprints_medio': sub['sprints'].mean()
        }
        perfis[jogador] = perfil

    return perfis
