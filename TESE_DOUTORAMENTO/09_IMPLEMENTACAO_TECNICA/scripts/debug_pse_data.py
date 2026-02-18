#!/usr/bin/env python3
"""
Debug PSE Data - Check What's Wrong
====================================

Checks why no metrics are being calculated from PSE data.
"""

import psycopg2
import os

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

def debug_pse_data():
    """Debug PSE data issues"""
    
    print("🔍 Debugging PSE Data")
    print("=" * 40)
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check total PSE records
        cursor.execute("SELECT COUNT(*) FROM dados_pse")
        pse_count = cursor.fetchone()[0]
        print(f"📊 Total PSE Records: {pse_count}")
        
        # Check sample PSE data
        cursor.execute("""
            SELECT dp.atleta_id, a.nome_completo, dp.sessao_id, s.data, dp.pse, dp.carga_total
            FROM dados_pse dp
            JOIN atletas a ON dp.atleta_id = a.id
            JOIN sessoes s ON dp.sessao_id = s.id
            LIMIT 10
        """)
        
        sample_pse = cursor.fetchall()
        
        print(f"\n📋 Sample PSE Records:")
        print("   Athlete | Name          | Session | Date       | PSE | Load")
        print("   --------|---------------|---------|------------|-----|------")
        
        for record in sample_pse:
            atleta_id, nome, sessao_id, date, pse, load = record
            print(f"   {atleta_id:7d} | {nome[:13]:13s} | {sessao_id:7d} | {date} | {pse:3.1f} | {load:5.0f}")
        
        # Check PSE data per athlete
        cursor.execute("""
            SELECT dp.atleta_id, a.nome_completo, COUNT(*) as record_count
            FROM dados_pse dp
            JOIN atletas a ON dp.atleta_id = a.id
            GROUP BY dp.atleta_id, a.nome_completo
            ORDER BY record_count DESC
            LIMIT 5
        """)
        
        athlete_counts = cursor.fetchall()
        
        print(f"\n👥 PSE Records per Athlete (Top 5):")
        for atleta_id, nome, count in athlete_counts:
            print(f"   {nome} (ID: {atleta_id}): {count} records")
        
        # Check if any athlete has enough data for metrics
        cursor.execute("""
            SELECT dp.atleta_id, a.nome_completo, COUNT(*) as record_count
            FROM dados_pse dp
            JOIN atletas a ON dp.atleta_id = a.id
            GROUP BY dp.atleta_id, a.nome_completo
            HAVING COUNT(*) >= 3
            ORDER BY record_count DESC
        """)
        
        qualified_athletes = cursor.fetchall()
        
        print(f"\n✅ Athletes with ≥3 PSE records: {len(qualified_athletes)}")
        for atleta_id, nome, count in qualified_athletes[:5]:
            print(f"   {nome} (ID: {atleta_id}): {count} records")
        
        # Check sessions per week
        cursor.execute("""
            SELECT DATE_TRUNC('week', s.data) as week, COUNT(*) as session_count
            FROM sessoes s
            GROUP BY DATE_TRUNC('week', s.data)
            ORDER BY week
        """)
        
        weekly_sessions = cursor.fetchall()
        
        print(f"\n📅 Sessions per Week:")
        for week, count in weekly_sessions:
            print(f"   Week of {week}: {count} sessions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    debug_pse_data()
