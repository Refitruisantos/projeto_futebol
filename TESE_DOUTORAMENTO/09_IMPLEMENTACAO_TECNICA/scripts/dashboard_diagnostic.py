#!/usr/bin/env python3
"""
Dashboard Diagnostic - Check Current Data
==========================================

Diagnoses why dashboard shows all red risks and empty graphs.
"""

import psycopg2
import os
import numpy as np

def get_db_connection():
    """Get direct database connection"""
    try:
        load_dotenv = __import__('dotenv').load_dotenv
        load_dotenv()
        
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5433'),
            database=os.getenv('DB_NAME', 'futebol_tese'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'desporto.20')
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def diagnose_dashboard():
    """Diagnose dashboard issues"""
    
    print("🔍 Dashboard Diagnostic")
    print("=" * 50)
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check athletes
        cursor.execute("SELECT COUNT(*) FROM atletas WHERE ativo = TRUE")
        athlete_count = cursor.fetchone()[0]
        print(f"📊 Active Athletes: {athlete_count}")
        
        # Check sessions
        cursor.execute("SELECT COUNT(*) FROM sessoes")
        session_count = cursor.fetchone()[0]
        print(f"📅 Total Sessions: {session_count}")
        
        # Check games
        cursor.execute("SELECT COUNT(*) FROM sessoes WHERE tipo = 'jogo'")
        game_count = cursor.fetchone()[0]
        print(f"⚽ Games: {game_count}")
        
        # Check metrics
        cursor.execute("SELECT COUNT(*) FROM metricas_carga")
        metrics_count = cursor.fetchone()[0]
        print(f"📈 Weekly Metrics: {metrics_count}")
        
        # Check risk distribution
        cursor.execute("""
            SELECT nivel_risco_monotonia, COUNT(*) 
            FROM metricas_carga 
            GROUP BY nivel_risco_monotonia
        """)
        risk_dist = cursor.fetchall()
        print(f"\n🚨 Risk Distribution (Monotony):")
        for risk, count in risk_dist:
            print(f"   {risk}: {count} athletes")
        
        # Sample metrics for analysis
        cursor.execute("""
            SELECT a.nome_completo, a.posicao, a.numero_camisola,
                   mc.carga_total_semanal, mc.monotonia, mc.tensao, mc.acwr,
                   mc.nivel_risco_monotonia, mc.nivel_risco_tensao, mc.nivel_risco_acwr,
                   mc.semana_inicio
            FROM metricas_carga mc
            JOIN atletas a ON mc.atleta_id = a.id
            WHERE mc.semana_inicio = (SELECT MAX(semana_inicio) FROM metricas_carga)
            ORDER BY mc.carga_total_semanal DESC
            LIMIT 5
        """)
        
        top_athletes = cursor.fetchall()
        
        print(f"\n🏆 Top 5 Athletes (Latest Week):")
        print("   Name                | Pos | # | Load  | Monotony | Strain | ACWR | Risks")
        print("   -------------------|-----|---|-------|----------|--------|------|-------")
        
        for athlete in top_athletes:
            nome, posicao, numero, carga, monotonia, tensao, acwr, risk_mono, risk_strain, risk_acwr, week = athlete
            risks = f"{risk_mono[0].upper()}/{risk_strain[0].upper()}/{risk_acwr[0].upper()}"
            print(f"   {nome[:18]:18s} | {posicao:3s} | {numero:2d} | {carga:5.0f} | {monotonia:8.2f} | {tensao:6.0f} | {acwr:4.2f} | {risks}")
        
        # Check data ranges
        cursor.execute("""
            SELECT 
                MIN(carga_total_semanal) as min_load,
                MAX(carga_total_semanal) as max_load,
                AVG(carga_total_semanal) as avg_load,
                MIN(monotonia) as min_monotony,
                MAX(monotonia) as max_monotony,
                AVG(monotonia) as avg_monotonia
            FROM metricas_carga
        """)
        
        ranges = cursor.fetchone()
        min_load, max_load, avg_load, min_monotony, max_monotony, avg_monotonia = ranges
        
        print(f"\n📊 Data Ranges:")
        print(f"   Load: {min_load:.0f} - {max_load:.0f} (avg: {avg_load:.0f})")
        print(f"   Monotony: {min_monotony:.2f} - {max_monotony:.2f} (avg: {avg_monotony:.2f})")
        
        # Risk threshold analysis
        print(f"\n⚠️  Risk Threshold Analysis:")
        print(f"   Current thresholds:")
        print(f"   - Monotony: <2.0 (Green), 2.0-3.0 (Yellow), >3.0 (Red)")
        print(f"   - Strain: <8000 (Green), 8000-12000 (Yellow), >12000 (Red)")
        print(f"   - ACWR: 0.8-1.5 (Green), 0.6-0.8 or 1.5-1.8 (Yellow), otherwise (Red)")
        
        # Suggest fixes
        if max_monotony > 3.0:
            print(f"\n💡 Suggestion: Many athletes have high monotony (>3.0)")
            print(f"   Consider adjusting training variation or risk thresholds")
        
        if avg_monotony > 2.5:
            print(f"💡 Suggestion: Average monotony is high ({avg_monotony:.2f})")
            print(f"   Training program may lack variation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    diagnose_dashboard()
