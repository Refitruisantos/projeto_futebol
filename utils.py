# Aqui podem ficar funções auxiliares como limpeza de dados, conversões, etc.

def normalizar_valores(df, colunas):
    for col in colunas:
        df[col] = (df[col] - df[col].mean()) / df[col].std()
    return df
