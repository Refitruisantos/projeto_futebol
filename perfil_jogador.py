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
        if 'aceleracoes' in sub.columns:
            perfil['aceleracoes_medias'] = sub['aceleracoes'].mean()
        if 'desaceleracoes' in sub.columns:
            perfil['desaceleracoes_medias'] = sub['desaceleracoes'].mean()
        if 'zona_alta_vel' in sub.columns:
            perfil['zona_alta_vel_media'] = sub['zona_alta_vel'].mean()
        if 'fc_media' in sub.columns:
            perfil['fc_media_media'] = sub['fc_media'].mean()
        perfis[jogador] = perfil

    return perfis
