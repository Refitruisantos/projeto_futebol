#!/usr/bin/env python3
"""
Check opponent difficulty classification system in database
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
    print("🔍 Checking opponent difficulty classification system...")
    
    try:
        db = DatabaseConnection()
        
        # Check if there's a table related to opponent difficulty
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%oppon%' OR table_name LIKE '%dificul%' OR table_name LIKE '%difficult%'
        """
        tables = db.query_to_dict(tables_query)
        
        print("📊 Tables related to opponent/difficulty:")
        print("-" * 50)
        for table in tables:
            print(f"- {table['table_name']}")
        
        # Check all tables to find the right one
        all_tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        all_tables = db.query_to_dict(all_tables_query)
        
        print(f"\n📋 All tables in database:")
        print("-" * 50)
        for table in all_tables:
            print(f"- {table['table_name']}")
        
        # Look for any table that might contain opponent difficulty data
        for table in all_tables:
            table_name = table['table_name']
            if 'oppon' in table_name.lower() or 'dificul' in table_name.lower() or 'difficult' in table_name.lower():
                print(f"\n🎯 Found potential table: {table_name}")
                
                # Get table structure
                columns_query = f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """
                columns = db.query_to_dict(columns_query)
                
                print(f"Columns in {table_name}:")
                for col in columns:
                    print(f"  - {col['column_name']}: {col['data_type']}")
                
                # Get sample data
                sample_query = f"SELECT * FROM {table_name} LIMIT 10"
                sample_data = db.query_to_dict(sample_query)
                
                print(f"\nSample data from {table_name}:")
                for row in sample_data[:5]:  # Show first 5 rows
                    print(f"  {row}")
        
        # Also check if there are any views or comments about opponent difficulty
        comments_query = """
            SELECT obj_description(oid) as description, relname as table_name
            FROM pg_class 
            WHERE relkind = 'r' 
            AND obj_description(oid) IS NOT NULL
            AND (obj_description(oid) ILIKE '%opponent%' OR obj_description(oid) ILIKE '%difficult%')
        """
        comments = db.query_to_dict(comments_query)
        
        if comments:
            print(f"\n💬 Tables with opponent/difficulty related comments:")
            print("-" * 60)
            for comment in comments:
                print(f"Table: {comment['table_name']}")
                print(f"Description: {comment['description']}")
                print("-" * 30)
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
