#!/usr/bin/env python3
"""
Delete session data from database - for manual data management
"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add python/ folder to system path for DB connection
parent_dir = Path(__file__).resolve().parent
python_dir = parent_dir / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

import importlib.util
module_path = python_dir / "01_conexao_db.py"
spec = importlib.util.spec_from_file_location("conexao_db", module_path)
conexao_db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conexao_db)
DatabaseConnection = conexao_db.DatabaseConnection

def list_sessions(jornada=None):
    """List all sessions, optionally filtered by jornada"""
    db = DatabaseConnection()
    
    if jornada:
        query = """
            SELECT s.id, s.data, s.tipo, s.jornada, s.created_at,
                   COUNT(DISTINCT g.id) as gps_records,
                   COUNT(DISTINCT p.id) as pse_records
            FROM sessoes s
            LEFT JOIN dados_gps g ON s.id = g.sessao_id
            LEFT JOIN dados_pse p ON s.id = p.sessao_id
            WHERE s.jornada = %s
            GROUP BY s.id, s.data, s.tipo, s.jornada, s.created_at
            ORDER BY s.created_at DESC
        """
        sessions = db.query_to_dict(query, (jornada,))
    else:
        query = """
            SELECT s.id, s.data, s.tipo, s.jornada, s.created_at,
                   COUNT(DISTINCT g.id) as gps_records,
                   COUNT(DISTINCT p.id) as pse_records
            FROM sessoes s
            LEFT JOIN dados_gps g ON s.id = g.sessao_id
            LEFT JOIN dados_pse p ON s.id = p.sessao_id
            GROUP BY s.id, s.data, s.tipo, s.jornada, s.created_at
            ORDER BY s.created_at DESC
            LIMIT 20
        """
        sessions = db.query_to_dict(query)
    
    db.close()
    
    print("📊 Sessions in database:")
    print("-" * 80)
    print(f"{'ID':<5} {'Date':<12} {'Type':<8} {'Jornada':<8} {'GPS':<5} {'PSE':<5} {'Created':<20}")
    print("-" * 80)
    
    for session in sessions:
        created = session['created_at'].strftime('%Y-%m-%d %H:%M') if session['created_at'] else 'N/A'
        print(f"{session['id']:<5} {session['data']:<12} {session['tipo']:<8} {session['jornada']:<8} {session['gps_records']:<5} {session['pse_records']:<5} {created:<20}")
    
    return sessions

def delete_session_data(session_id):
    """Delete all data for a specific session"""
    db = DatabaseConnection()
    
    try:
        # Get session info first
        session_query = "SELECT id, data, tipo, jornada FROM sessoes WHERE id = %s"
        session = db.query_to_dict(session_query, (session_id,))
        
        if not session:
            print(f"❌ Session {session_id} not found")
            return False
        
        session_info = session[0]
        print(f"🗑️ Deleting session {session_id}: {session_info['data']} - Jornada {session_info['jornada']}")
        
        # Count records before deletion
        gps_count_query = "SELECT COUNT(*) as count FROM dados_gps WHERE sessao_id = %s"
        pse_count_query = "SELECT COUNT(*) as count FROM dados_pse WHERE sessao_id = %s"
        
        gps_count = db.query_to_dict(gps_count_query, (session_id,))[0]['count']
        pse_count = db.query_to_dict(pse_count_query, (session_id,))[0]['count']
        
        print(f"📊 Will delete: {gps_count} GPS records, {pse_count} PSE records")
        
        # Delete in correct order (foreign key constraints)
        print("🗑️ Deleting GPS data...")
        db.execute_query("DELETE FROM dados_gps WHERE sessao_id = %s", (session_id,))
        
        print("🗑️ Deleting PSE data...")
        db.execute_query("DELETE FROM dados_pse WHERE sessao_id = %s", (session_id,))
        
        print("🗑️ Deleting session...")
        db.execute_query("DELETE FROM sessoes WHERE id = %s", (session_id,))
        
        db.close()
        
        print(f"✅ Session {session_id} deleted successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting session {session_id}: {e}")
        db.close()
        return False

def delete_jornada_data(jornada):
    """Delete all data for a specific jornada"""
    db = DatabaseConnection()
    
    try:
        # Get sessions for this jornada
        sessions_query = "SELECT id, data, tipo FROM sessoes WHERE jornada = %s"
        sessions = db.query_to_dict(sessions_query, (jornada,))
        
        if not sessions:
            print(f"❌ No sessions found for Jornada {jornada}")
            return False
        
        print(f"🗑️ Found {len(sessions)} sessions for Jornada {jornada}")
        
        # Count total records
        total_gps = 0
        total_pse = 0
        
        for session in sessions:
            gps_count = db.query_to_dict("SELECT COUNT(*) as count FROM dados_gps WHERE sessao_id = %s", (session['id'],))[0]['count']
            pse_count = db.query_to_dict("SELECT COUNT(*) as count FROM dados_pse WHERE sessao_id = %s", (session['id'],))[0]['count']
            total_gps += gps_count
            total_pse += pse_count
        
        print(f"📊 Will delete: {total_gps} GPS records, {total_pse} PSE records, {len(sessions)} sessions")
        
        # Delete all data for this jornada
        print("🗑️ Deleting GPS data...")
        db.execute_query("DELETE FROM dados_gps WHERE sessao_id IN (SELECT id FROM sessoes WHERE jornada = %s)", (jornada,))
        
        print("🗑️ Deleting PSE data...")
        db.execute_query("DELETE FROM dados_pse WHERE sessao_id IN (SELECT id FROM sessoes WHERE jornada = %s)", (jornada,))
        
        print("🗑️ Deleting sessions...")
        db.execute_query("DELETE FROM sessoes WHERE jornada = %s", (jornada,))
        
        db.close()
        
        print(f"✅ All Jornada {jornada} data deleted successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting Jornada {jornada}: {e}")
        db.close()
        return False

def main():
    """Interactive session management"""
    print("🗂️ Session Data Management Tool")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. List all recent sessions")
        print("2. List sessions for specific jornada")
        print("3. Delete specific session")
        print("4. Delete all data for jornada")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            list_sessions()
            
        elif choice == "2":
            jornada = input("Enter jornada number: ").strip()
            try:
                jornada_num = int(jornada)
                list_sessions(jornada_num)
            except ValueError:
                print("❌ Invalid jornada number")
                
        elif choice == "3":
            session_id = input("Enter session ID to delete: ").strip()
            try:
                session_id_num = int(session_id)
                confirm = input(f"Are you sure you want to delete session {session_id_num}? (yes/no): ").strip().lower()
                if confirm == "yes":
                    delete_session_data(session_id_num)
                else:
                    print("❌ Deletion cancelled")
            except ValueError:
                print("❌ Invalid session ID")
                
        elif choice == "4":
            jornada = input("Enter jornada number to delete completely: ").strip()
            try:
                jornada_num = int(jornada)
                confirm = input(f"Are you sure you want to delete ALL data for Jornada {jornada_num}? (yes/no): ").strip().lower()
                if confirm == "yes":
                    delete_jornada_data(jornada_num)
                else:
                    print("❌ Deletion cancelled")
            except ValueError:
                print("❌ Invalid jornada number")
                
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
