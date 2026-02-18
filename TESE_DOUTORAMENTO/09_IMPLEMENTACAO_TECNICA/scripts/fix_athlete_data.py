#!/usr/bin/env python3
"""
Fix Athlete Data - Add Missing Jersey Numbers
==============================================

Updates athletes with proper jersey numbers for identification.
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

def fix_athlete_data():
    """Add jersey numbers and fix athlete identification"""
    
    print("🔄 Fixing athlete data...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Get current athletes
        cursor.execute("""
            SELECT id, nome_completo, posicao, numero_camisola 
            FROM atletas 
            WHERE ativo = TRUE 
            ORDER BY id
        """)
        athletes = cursor.fetchall()
        
        print(f"   Found {len(athletes)} athletes")
        
        # Assign jersey numbers by position
        jersey_assignments = {
            'GR': [1, 12, 25, 33],      # Goalkeepers
            'DC': [2, 3, 4, 5, 13, 14, 15, 16, 18, 22, 24, 26, 27, 28, 29, 30, 31, 32, 34, 35],  # Defenders
            'DL': [20, 21, 23, 40, 41, 42],  # Wing-backs
            'MC': [6, 7, 8, 10, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],  # Midfielders
            'EX': [11, 14, 15, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],  # Wingers
            'AV': [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]  # Forwards
        }
        
        position_counters = {pos: 0 for pos in jersey_assignments.keys()}
        
        for athlete_id, nome, posicao, current_number in athletes:
            if current_number is None or current_number == 0:
                # Assign next available jersey number for this position
                counter = position_counters[posicao]
                if counter < len(jersey_assignments[posicao]):
                    new_number = jersey_assignments[posicao][counter]
                    position_counters[posicao] += 1
                    
                    cursor.execute("""
                        UPDATE atletas 
                        SET numero_camisola = %s 
                        WHERE id = %s
                    """, (new_number, athlete_id))
                    
                    print(f"   {nome} ({posicao}) → Jersey #{new_number}")
                else:
                    # Fallback: use ID + 100
                    cursor.execute("""
                        UPDATE atletas 
                        SET numero_camisola = %s 
                        WHERE id = %s
                    """, (athlete_id + 100, athlete_id))
                    
                    print(f"   {nome} ({posicao}) → Jersey #{athlete_id + 100} (fallback)")
            else:
                print(f"   {nome} ({posicao}) → Already has Jersey #{current_number}")
        
        conn.commit()
        
        # Verify the updates
        cursor.execute("""
            SELECT id, nome_completo, posicao, numero_camisola 
            FROM atletas 
            WHERE ativo = TRUE 
            ORDER BY numero_camisola
        """)
        updated_athletes = cursor.fetchall()
        
        print(f"\n✅ Updated athlete data:")
        print("   ID  | Name                | Pos | Jersey")
        print("   ----|---------------------|-----|--------")
        for athlete_id, nome, posicao, jersey in updated_athletes:
            print(f"   {athlete_id:3d} | {nome[:19]:19s} | {posicao:3s} | {jersey:3d}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if fix_athlete_data():
        print("\n🚀 Athlete data fixed!")
        print("   Jersey numbers assigned for proper identification.")
        print("   Refresh your browser to see athlete IDs in the dashboard.")
    else:
        print("\n❌ Failed to fix athlete data")
