#!/usr/bin/env python3
"""
Check what's actually stored in sessions table for training types
"""
import sys
from pathlib import Path

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

def main():
    print("🔍 Checking session data for training types...")
    
    try:
        db = DatabaseConnection()
        
        # Get recent sessions to see what's stored
        query = """
            SELECT id, data, tipo, competicao, jornada, created_at
            FROM sessoes 
            ORDER BY created_at DESC 
            LIMIT 10
        """
        sessions = db.query_to_dict(query)
        
        print("📊 Recent sessions:")
        print("-" * 80)
        print(f"{'ID':<4} {'Date':<12} {'Tipo':<12} {'Competicao':<25} {'Jornada':<8}")
        print("-" * 80)
        
        for session in sessions:
            print(f"{session['id']:<4} {str(session['data']):<12} {session['tipo']:<12} {str(session['competicao']):<25} {str(session['jornada']):<8}")
        
        # Check specifically for sessions with training descriptions
        training_query = """
            SELECT tipo, competicao, COUNT(*) as count
            FROM sessoes 
            WHERE competicao IS NOT NULL
            GROUP BY tipo, competicao
            ORDER BY count DESC
        """
        training_types = db.query_to_dict(training_query)
        
        print(f"\n📋 Training type combinations:")
        print("-" * 60)
        print(f"{'Tipo':<15} {'Competicao':<30} {'Count':<8}")
        print("-" * 60)
        
        for tt in training_types:
            print(f"{tt['tipo']:<15} {str(tt['competicao']):<30} {tt['count']:<8}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
