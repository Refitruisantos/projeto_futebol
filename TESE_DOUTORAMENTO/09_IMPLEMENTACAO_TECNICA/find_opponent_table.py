#!/usr/bin/env python3
"""
Find the correct opponent difficulty table name in database
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

def find_opponent_table():
    print("🔍 Finding opponent difficulty table...")
    
    try:
        db = DatabaseConnection()
        
        # Get all tables
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        tables = db.query_to_dict(tables_query)
        
        print("📊 All tables in database:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Look for tables that might contain opponent data
        opponent_tables = []
        for table in tables:
            table_name = table['table_name']
            if any(keyword in table_name.lower() for keyword in ['opponent', 'adversar', 'dificul', 'difficult']):
                opponent_tables.append(table_name)
        
        if opponent_tables:
            print(f"\n🎯 Found potential opponent tables:")
            for table_name in opponent_tables:
                print(f"  - {table_name}")
                
                # Check table structure
                columns_query = f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """
                columns = db.query_to_dict(columns_query)
                
                print(f"    Columns:")
                for col in columns:
                    print(f"      - {col['column_name']}: {col['data_type']}")
                
                # Get sample data
                try:
                    sample_query = f"SELECT * FROM {table_name} LIMIT 3"
                    sample_data = db.query_to_dict(sample_query)
                    
                    if sample_data:
                        print(f"    Sample data:")
                        for i, row in enumerate(sample_data):
                            print(f"      Row {i+1}: {dict(row)}")
                    else:
                        print(f"    No data in table")
                except Exception as e:
                    print(f"    Error reading data: {e}")
                
                print()
        else:
            print("\n❌ No obvious opponent difficulty tables found")
            print("Let me check if there are any tables with opponent-related data...")
            
            # Check for any table that might have opponent names
            for table in tables:
                table_name = table['table_name']
                try:
                    # Check if table has columns that might contain opponent data
                    columns_query = f"""
                        SELECT column_name
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name}'
                        AND (column_name ILIKE '%opponent%' OR column_name ILIKE '%adversar%' 
                             OR column_name ILIKE '%rating%' OR column_name ILIKE '%difficult%')
                    """
                    relevant_columns = db.query_to_dict(columns_query)
                    
                    if relevant_columns:
                        print(f"Table '{table_name}' has relevant columns:")
                        for col in relevant_columns:
                            print(f"  - {col['column_name']}")
                        
                        # Get sample data
                        sample_query = f"SELECT * FROM {table_name} LIMIT 2"
                        sample_data = db.query_to_dict(sample_query)
                        
                        if sample_data:
                            print(f"Sample data:")
                            for row in sample_data:
                                print(f"  {dict(row)}")
                        print()
                        
                except Exception:
                    continue
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    find_opponent_table()
