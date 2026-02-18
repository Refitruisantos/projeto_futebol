#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar os jogadores reais do PDF GPS à base de dados
Substitui os dados fictícios por dados reais da equipa
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.database import get_db
from datetime import date

def jogadores_pdf_gps():
    """
    Jogadores reais extraídos do PDF GPS (JOGO_2ªJORNADA)
    """
    return [
        {
            'jogador_id': 'DUARTE_CALHA',
            'nome_completo': 'Duarte Calha',
            'posicao': 'DC',  # Assumindo posição baseada no desempenho
            'numero_camisola': 4,
            'pe_dominante': 'Direito'
        },
        {
            'jogador_id': 'GABI_COELHO',
            'nome_completo': 'Gabi Coelho',
            'posicao': 'AV',
            'numero_camisola': 9,
            'pe_dominante': 'Direito'
        },
        {
            'jogador_id': 'GONCALO_CARDOSO',
            'nome_completo': 'Gonçalo Cardoso',
            'posicao': 'DC',
            'numero_camisola': 3,
            'pe_dominante': 'Direito'
        },
        {
            'jogador_id': 'GONCALO_GR',
            'nome_completo': 'Gonçalo',
            'posicao': 'GR',
            'numero_camisola': 1,
            'pe_dominante': 'Direito'
        },
        {
            'jogador_id': 'JOAO_FERREIRA',
            'nome_completo': 'João Ferreira',
            'posicao': 'MC',
            'numero_camisola': 8,
            'pe_dominante': 'Direito'
        },
        {
            'jogador_id': 'LEONARDO_SANTOS',
            'nome_completo': 'Leonardo Santos',
            'posicao': 'DC',
            'numero_camisola': 2,
            'pe_dominante': 'Esquerdo'
        },
        {
            'jogador_id': 'LESIANDRO_MARINHO',
            'nome_completo': 'Lesiandro Marinho',
            'posicao': 'EX',
            'numero_camisola': 7,
            'pe_dominante': 'Esquerdo'
        },
        {
            'jogador_id': 'MARTIM_SOARES',
            'nome_completo': 'Martim Soares',
            'posicao': 'AV',
            'numero_camisola': 11,
            'pe_dominante': 'Direito'
        },
        {
            'jogador_id': 'PAULO_DANIEL',
            'nome_completo': 'Paulo Daniel',
            'posicao': 'MC',
            'numero_camisola': 6,
            'pe_dominante': 'Direito'
        },
        {
            'jogador_id': 'PEDRO_RIBEIRO',
            'nome_completo': 'Pedro Ribeiro',
            'posicao': 'EX',
            'numero_camisola': 10,
            'pe_dominante': 'Esquerdo'
        },
        {
            'jogador_id': 'RAFAEL_DIAS',
            'nome_completo': 'Rafael Dias',
            'posicao': 'DL',
            'numero_camisola': 5,
            'pe_dominante': 'Direito'
        },
        {
            'jogador_id': 'RAFAEL_CESARIO',
            'nome_completo': 'Rafael Cesário',
            'posicao': 'MC',
            'numero_camisola': 14,
            'pe_dominante': 'Direito'
        },
        {
            'jogador_id': 'RODRIGO_ANDRADE',
            'nome_completo': 'Rodrigo Andrade',
            'posicao': 'EX',
            'numero_camisola': 17,
            'pe_dominante': 'Esquerdo'
        },
        {
            'jogador_id': 'TIAGO_BATISTA',
            'nome_completo': 'Tiago Batista',
            'posicao': 'DC',
            'numero_camisola': 15,
            'pe_dominante': 'Direito'
        },
        {
            'jogador_id': 'TIAGO_LOBO',
            'nome_completo': 'Tiago Lobo',
            'posicao': 'DL',
            'numero_camisola': 12,
            'pe_dominante': 'Esquerdo'
        }
    ]

def limpar_dados_ficticios():
    """
    Remove os dados fictícios existentes (opcional)
    """
    print("🗑️  Limpando dados fictícios...")
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Desativar atletas fictícios em vez de eliminar (preserva integridade)
        deactivate_query = "UPDATE atletas SET ativo = false WHERE jogador_id LIKE 'ATL%'"
        db.execute_query(deactivate_query)
        
        # Contar quantos foram desativados
        count_query = "SELECT COUNT(*) as count FROM atletas WHERE jogador_id LIKE 'ATL%' AND ativo = false"
        result = db.query_to_dict(count_query)
        count = result[0]['count'] if result else 0
        
        print(f"✓ {count} atletas fictícios desativados")
        
        return count
        
    except Exception as e:
        print(f"❌ Erro ao limpar dados fictícios: {str(e)}")
        return 0
    
    finally:
        db.close()

def adicionar_jogadores_reais(limpar_ficticios=True):
    """
    Adiciona os jogadores reais à base de dados
    """
    
    print("🏃 Adicionando jogadores reais à base de dados...")
    
    if limpar_ficticios:
        limpar_dados_ficticios()
    
    jogadores = jogadores_pdf_gps()
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        adicionados = 0
        erros = []
        
        for jogador in jogadores:
            try:
                # Verificar se já existe
                check_query = "SELECT id FROM atletas WHERE jogador_id = %s"
                existing = db.query_to_dict(check_query, (jogador['jogador_id'],))
                
                if existing:
                    print(f"⚠️  Jogador {jogador['nome_completo']} já existe")
                    continue
                
                # Verificar se número da camisola está ocupado
                if jogador.get('numero_camisola'):
                    number_query = "SELECT id, nome_completo FROM atletas WHERE numero_camisola = %s AND ativo = true"
                    number_conflict = db.query_to_dict(number_query, (jogador['numero_camisola'],))
                    
                    if number_conflict:
                        print(f"⚠️  Número {jogador['numero_camisola']} já ocupado por {number_conflict[0]['nome_completo']}")
                        # Remover número da camisola para evitar conflito
                        jogador['numero_camisola'] = None
                
                # Inserir jogador
                insert_query = """
                    INSERT INTO atletas (
                        jogador_id, nome_completo, posicao, numero_camisola, 
                        pe_dominante, ativo, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, true, NOW(), NOW()
                    )
                """
                
                db.execute_query(insert_query, (
                    jogador['jogador_id'],
                    jogador['nome_completo'],
                    jogador['posicao'],
                    jogador.get('numero_camisola'),
                    jogador.get('pe_dominante')
                ))
                
                print(f"✅ {jogador['nome_completo']} adicionado (#{jogador.get('numero_camisola', 'S/N')})")
                adicionados += 1
                
            except Exception as e:
                erro_msg = f"Erro ao adicionar {jogador['nome_completo']}: {str(e)}"
                erros.append(erro_msg)
                print(f"❌ {erro_msg}")
        
        print(f"\n🎉 Processamento concluído!")
        print(f"  - Jogadores adicionados: {adicionados}/{len(jogadores)}")
        
        if erros:
            print(f"  - Erros: {len(erros)}")
            for erro in erros[:3]:  # Mostrar apenas os primeiros 3
                print(f"    • {erro}")
        
        return {
            "success": True,
            "adicionados": adicionados,
            "total": len(jogadores),
            "erros": erros
        }
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()

def verificar_jogadores_adicionados():
    """
    Verifica os jogadores que foram adicionados
    """
    print("\n📋 Verificando jogadores na base de dados...")
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Jogadores ativos
        query_ativos = """
            SELECT jogador_id, nome_completo, posicao, numero_camisola, pe_dominante
            FROM atletas 
            WHERE ativo = true 
            ORDER BY numero_camisola, nome_completo
        """
        
        ativos = db.query_to_dict(query_ativos)
        
        print(f"\n✅ Jogadores Ativos ({len(ativos)}):")
        print("-" * 70)
        
        for jogador in ativos:
            numero = f"#{jogador['numero_camisola']:2d}" if jogador['numero_camisola'] else "#--"
            posicao = jogador['posicao'] or "---"
            pe = jogador['pe_dominante'] or "---"
            
            print(f"{numero} | {jogador['nome_completo']:20s} | {posicao:3s} | {pe:10s} | {jogador['jogador_id']}")
        
        # Jogadores inativos (fictícios)
        query_inativos = """
            SELECT COUNT(*) as count 
            FROM atletas 
            WHERE ativo = false
        """
        
        inativos = db.query_to_dict(query_inativos)
        count_inativos = inativos[0]['count'] if inativos else 0
        
        if count_inativos > 0:
            print(f"\n⚠️  Jogadores Inativos (fictícios): {count_inativos}")
        
        return ativos
        
    except Exception as e:
        print(f"❌ Erro ao verificar jogadores: {str(e)}")
        return []
    
    finally:
        db.close()

if __name__ == '__main__':
    print("🚀 Configuração de Jogadores Reais")
    print("=" * 50)
    
    # Adicionar jogadores reais
    resultado = adicionar_jogadores_reais(limpar_ficticios=True)
    
    if resultado["success"]:
        # Verificar resultado
        jogadores = verificar_jogadores_adicionados()
        
        print(f"\n✅ Configuração concluída!")
        print(f"   Agora pode:")
        print(f"   1. Usar a interface web para gerir atletas")
        print(f"   2. Carregar dados GPS reais dos jogadores")
        print(f"   3. Visualizar dashboards com dados reais")
        print(f"\n🌐 Interface: http://localhost:5173/athletes")
        
    else:
        print(f"\n❌ Falha na configuração: {resultado['error']}")
