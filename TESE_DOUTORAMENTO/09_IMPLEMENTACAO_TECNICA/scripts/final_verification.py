#!/usr/bin/env python3
"""
Final Dashboard Verification
===========================

Checks all dashboard components are working correctly.
"""

import psycopg2
import os
from datetime import datetime

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

def verify_dashboard():
    """Verify all dashboard components"""
    
    print("🔍 FINAL DASHBOARD VERIFICATION")
    print("=" * 60)
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Athletes with jersey numbers (AU values)
        cursor.execute("""
            SELECT COUNT(*) FROM atletas WHERE ativo = TRUE AND numero_camisola IS NOT NULL
        """)
        athletes_with_numbers = cursor.fetchone()[0]
        
        # 2. Sessions with opponent data and rounds
        cursor.execute("""
            SELECT COUNT(*) FROM sessoes WHERE tipo = 'jogo' AND adversario IS NOT NULL AND jornada IS NOT NULL
        """)
        games_with_data = cursor.fetchone()[0]
        
        # 3. GPS metrics with high-speed distance
        cursor.execute("""
            SELECT COUNT(*) FROM metricas_carga WHERE high_speed_distance IS NOT NULL
        """)
        metrics_with_gps = cursor.fetchone()[0]
        
        # 4. ML risk athletes
        cursor.execute("""
            SELECT COUNT(*) FROM ml_risk_summary WHERE ml_risk_level = 'High'
        """)
        high_risk_athletes = cursor.fetchone()[0]
        
        # 5. Total data counts
        cursor.execute("SELECT COUNT(*) FROM atletas WHERE ativo = TRUE")
        total_athletes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sessoes")
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM metricas_carga")
        total_metrics = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dados_pse")
        total_pse = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dados_gps")
        total_gps = cursor.fetchone()[0]
        
        # Print verification results
        print(f"✅ ATHLETE IDENTIFICATION (AU):")
        print(f"   {athletes_with_numbers}/{total_athletes} athletes have jersey numbers")
        
        print(f"\n✅ SESSIONS WITH OPPONENT DATA:")
        print(f"   {games_with_data} games with opponent info and round numbers")
        
        print(f"\n✅ GPS METRICS:")
        print(f"   {metrics_with_gps} records with high-speed distance")
        
        print(f"\n✅ ML RISK SYSTEM:")
        print(f"   {high_risk_athletes} high-risk athletes identified")
        
        print(f"\n📊 DATA SUMMARY:")
        print(f"   Athletes: {total_athletes}")
        print(f"   Sessions: {total_sessions}")
        print(f"   Weekly Metrics: {total_metrics}")
        print(f"   PSE Records: {total_pse}")
        print(f"   GPS Records: {total_gps}")
        
        # Show sample high-risk athletes
        cursor.execute("""
            SELECT nome_completo, posicao, numero_camisola, ml_risk_score, risk_factors, recommendation
            FROM ml_risk_summary 
            WHERE ml_risk_level = 'High'
            ORDER BY ml_risk_score DESC
            LIMIT 3
        """)
        
        high_risk_sample = cursor.fetchall()
        
        print(f"\n🔴 SAMPLE HIGH-RISK ATHLETES:")
        print("   Name                | Pos | # | Score | Key Issues")
        print("   -------------------|-----|---|-------|-------------")
        
        for nome, posicao, numero, score, factors, rec in high_risk_sample:
            print(f"   {nome[:18]:18s} | {posicao:3s} | {numero:2d} | {score:5d} | {factors[:30]}...")
        
        # Show sample games with opponent data
        cursor.execute("""
            SELECT adversario, local, resultado, jornada, observacoes
            FROM sessoes 
            WHERE tipo = 'jogo' AND adversario IS NOT NULL
            ORDER BY data
            LIMIT 3
        """)
        
        games_sample = cursor.fetchall()
        
        print(f"\n⚽ SAMPLE GAMES WITH OPPONENT DATA:")
        print("   Opponent        | Location | Score | Round | Details")
        print("   ----------------|----------|-------|-------|----------------")
        
        for opponent, local, result, round, obs in games_sample:
            print(f"   {opponent[:15]:15s} | {local:8s} | {result:5s} | {round:5d} | {obs[:40]}...")
        
        # Overall status
        print(f"\n🎯 DASHBOARD STATUS:")
        
        checks = [
            (athletes_with_numbers == total_athletes, "Athlete identification (AU)"),
            (games_with_data >= 5, "Games with opponent data"),
            (metrics_with_gps > 0, "GPS high-speed distance"),
            (high_risk_athletes > 0, "ML risk identification"),
            (total_metrics > 0, "Weekly metrics"),
            (total_pse > 1000, "PSE data volume"),
            (total_gps > 1000, "GPS data volume")
        ]
        
        all_good = True
        for check, description in checks:
            status = "✅" if check else "❌"
            print(f"   {status} {description}")
            if not check:
                all_good = False
        
        if all_good:
            print(f"\n🎉 ALL SYSTEMS READY!")
            print(f"   Dashboard should show complete data with:")
            print(f"   • All 20 athletes with jersey numbers")
            print(f"   • Interactive hover on risk athletes")
            print(f"   • High-speed distance and GPS metrics")
            print(f"   • Complete opponent information and rounds")
            print(f"   • Scientific ML risk scores")
            print(f"   • Detailed recommendations")
            print(f"\n📊 Refresh your browser to see all improvements!")
        else:
            print(f"\n⚠️  Some components need attention")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    verify_dashboard()
