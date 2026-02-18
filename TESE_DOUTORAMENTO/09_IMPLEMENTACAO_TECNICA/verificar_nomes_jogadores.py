#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar nomes dos jogadores na base de dados
e criar mapeamento correto para o PDF GPS
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.database import get_db

def verificar_jogadores_bd():
    """Verifica que jogadores existem na base de dados"""
    
    print("🔍 Verificando jogadores na base de dados...")
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Obter todos os jogadores ativos
        query = """
            SELECT id, nome_completo, jogador_id, posicao
            FROM atletas
            WHERE ativo = true
            ORDER BY nome_completo
        """
        
        jogadores = db.query_to_dict(query)
        
        print(f"\n✅ Encontrados {len(jogadores)} jogadores ativos:")
        print("-" * 60)
        
        for jogador in jogadores:
            print(f"ID: {jogador['id']:3d} | Nome: {jogador['nome_completo']:25s} | Jogador ID: {jogador['jogador_id']:15s} | Pos: {jogador['posicao'] or 'N/A'}")
        
        return jogadores
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return []
    
    finally:
        db.close()

def nomes_pdf():
    """Nomes que aparecem no PDF GPS"""
    return [
        'DUARTE CALHA',
        'GABI COELHO', 
        'GONÇALO CARDOSO',
        'GONÇALO GR',
        'JOÃO FERREIRA',
        'LEONARDO SANTOS',
        'LESIANDRO MARINHO',
        'MARTIM SOARES',
        'PAULO DANIEL',
        'PEDRO RIBEIRO',
        'RAFAEL DIAS',
        'RAFAEL CESÁRIO',
        'RODRIGO ANDRADE',
        'TIAGO BATISTA',
        'TIAGO LOBO'
    ]

def criar_mapeamento(jogadores_bd, nomes_pdf_list):
    """Cria mapeamento entre nomes do PDF e base de dados"""
    
    print(f"\n🔗 Criando mapeamento entre PDF e base de dados...")
    print("-" * 60)
    
    mapeamento = {}
    nao_encontrados = []
    
    for nome_pdf in nomes_pdf_list:
        encontrado = False
        
        # Tentar correspondência exata
        for jogador in jogadores_bd:
            if (nome_pdf.lower() == jogador['nome_completo'].lower() or 
                nome_pdf.lower() == jogador['jogador_id'].lower()):
                mapeamento[nome_pdf] = jogador
                print(f"✅ {nome_pdf:20s} -> {jogador['nome_completo']}")
                encontrado = True
                break
        
        # Tentar correspondência parcial
        if not encontrado:
            for jogador in jogadores_bd:
                nome_bd = jogador['nome_completo'].lower()
                nome_pdf_lower = nome_pdf.lower()
                
                # Verificar se contém palavras em comum
                palavras_pdf = nome_pdf_lower.split()
                palavras_bd = nome_bd.split()
                
                # Se pelo menos 2 palavras coincidem ou nome muito similar
                coincidencias = sum(1 for p in palavras_pdf if any(p in bd for bd in palavras_bd))
                
                if coincidencias >= 2 or any(p in nome_bd for p in palavras_pdf if len(p) > 3):
                    mapeamento[nome_pdf] = jogador
                    print(f"🔍 {nome_pdf:20s} -> {jogador['nome_completo']} (parcial)")
                    encontrado = True
                    break
        
        if not encontrado:
            nao_encontrados.append(nome_pdf)
            print(f"❌ {nome_pdf:20s} -> NÃO ENCONTRADO")
    
    if nao_encontrados:
        print(f"\n⚠️  Jogadores não encontrados ({len(nao_encontrados)}):")
        for nome in nao_encontrados:
            print(f"   - {nome}")
        
        print(f"\n💡 Sugestões:")
        print(f"   1. Verificar se estes jogadores existem na tabela 'atletas'")
        print(f"   2. Verificar se os nomes estão escritos corretamente")
        print(f"   3. Adicionar estes jogadores à base de dados se necessário")
    
    return mapeamento, nao_encontrados

if __name__ == '__main__':
    # Verificar jogadores na BD
    jogadores_bd = verificar_jogadores_bd()
    
    if not jogadores_bd:
        print("❌ Nenhum jogador encontrado na base de dados!")
        exit(1)
    
    # Obter nomes do PDF
    nomes_pdf_list = nomes_pdf()
    
    # Criar mapeamento
    mapeamento, nao_encontrados = criar_mapeamento(jogadores_bd, nomes_pdf_list)
    
    print(f"\n📊 Resumo:")
    print(f"   - Jogadores na BD: {len(jogadores_bd)}")
    print(f"   - Jogadores no PDF: {len(nomes_pdf_list)}")
    print(f"   - Mapeamentos encontrados: {len(mapeamento)}")
    print(f"   - Não encontrados: {len(nao_encontrados)}")
    
    if len(mapeamento) > 0:
        print(f"\n✅ Pode processar {len(mapeamento)} jogadores automaticamente!")
    else:
        print(f"\n❌ Nenhum mapeamento encontrado. Verificar nomes na base de dados.")
