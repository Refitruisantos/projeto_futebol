#!/usr/bin/env python3
"""
Extract all opponent difficulty data from database for manual recreation
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

def extract_opponent_data():
    print("🔍 Extracting opponent difficulty data for manual recreation...")
    
    try:
        db = DatabaseConnection()
        
        # Get all opponent difficulty records
        query = """
            SELECT 
                id,
                opponent_name,
                league_position,
                recent_form_points,
                home_advantage,
                head_to_head_record,
                key_players_available,
                tactical_difficulty,
                physical_intensity,
                overall_rating,
                explanation,
                detailed_breakdown
            FROM opponent_difficulty 
            ORDER BY overall_rating DESC
        """
        opponents = db.query_to_dict(query)
        
        print(f"📊 Found {len(opponents)} opponents in database")
        print("=" * 80)
        
        manual_data = []
        
        for i, opp in enumerate(opponents, 1):
            print(f"\n🎯 OPPONENT {i}: {opp['opponent_name']}")
            print("-" * 60)
            
            # Extract raw data for manual entry
            raw_data = {
                'opponent_name': opp['opponent_name'],
                'league_position': opp['league_position'],
                'recent_form_points': opp['recent_form_points'],
                'venue': 'Home' if opp['home_advantage'] else 'Away',
                'h2h_record': opp['head_to_head_record'],
                'key_players': opp['key_players_available'],
                'tactical_score': opp['tactical_difficulty'],
                'physical_score': opp['physical_intensity'],
                'final_rating': float(opp['overall_rating'])
            }
            
            print(f"Raw Data for Manual Entry:")
            print(f"  League Position: {raw_data['league_position']}")
            print(f"  Recent Form Points: {raw_data['recent_form_points']}")
            print(f"  Venue: {raw_data['venue']}")
            print(f"  H2H Record: {raw_data['h2h_record']}")
            print(f"  Key Players Available: {raw_data['key_players']}")
            print(f"  Tactical Difficulty: {raw_data['tactical_score']}")
            print(f"  Physical Intensity: {raw_data['physical_score']}")
            print(f"  Expected Final Rating: {raw_data['final_rating']}")
            
            # Calculate step-by-step for verification
            print(f"\nStep-by-Step Manual Calculation:")
            
            # 1. League Position (25%)
            league_score = 1 - (raw_data['league_position'] - 1) / 19
            league_points = league_score * 25
            print(f"  1. League Position: {raw_data['league_position']} → {league_score:.3f} × 25% = {league_points:.1f} pts")
            
            # 2. Recent Form (20%)
            form_score = raw_data['recent_form_points'] / 15
            form_points = form_score * 20
            print(f"  2. Recent Form: {raw_data['recent_form_points']} pts → {form_score:.3f} × 20% = {form_points:.1f} pts")
            
            # 3. Home/Away (15%)
            venue_score = 1.0 if raw_data['venue'] == 'Home' else 0.8
            venue_points = venue_score * 15
            print(f"  3. Venue: {raw_data['venue']} → {venue_score:.1f} × 15% = {venue_points:.1f} pts")
            
            # 4. H2H Record (15%) - need to parse the record
            h2h_record = raw_data['h2h_record']
            if 'W' in h2h_record and 'D' in h2h_record and 'L' in h2h_record:
                # Parse format like "3W-1D-1L"
                parts = h2h_record.replace('W', '').replace('D', '').replace('L', '').split('-')
                if len(parts) == 3:
                    wins, draws, losses = map(int, parts)
                    total_games = wins + draws + losses
                    h2h_score = (wins * 3 + draws * 1) / (total_games * 3) if total_games > 0 else 0.5
                else:
                    h2h_score = 0.5  # default
            else:
                h2h_score = 0.5  # default for unclear records
            h2h_points = h2h_score * 15
            print(f"  4. H2H Record: {h2h_record} → {h2h_score:.3f} × 15% = {h2h_points:.1f} pts")
            
            # 5. Key Players (10%)
            players_score = raw_data['key_players'] / 11
            players_points = players_score * 10
            print(f"  5. Key Players: {raw_data['key_players']}/11 → {players_score:.3f} × 10% = {players_points:.1f} pts")
            
            # 6. Tactical Complexity (10%)
            tactical_score = raw_data['tactical_score'] / 5  # Convert 1-5 scale to 0-1
            tactical_points = tactical_score * 10
            print(f"  6. Tactical: {raw_data['tactical_score']}/5 → {tactical_score:.3f} × 10% = {tactical_points:.1f} pts")
            
            # 7. Physical Intensity (5%)
            physical_score = raw_data['physical_score'] / 5  # Convert 1-5 scale to 0-1
            physical_points = physical_score * 5
            print(f"  7. Physical: {raw_data['physical_score']}/5 → {physical_score:.3f} × 5% = {physical_points:.1f} pts")
            
            # Total calculation
            total_points = league_points + form_points + venue_points + h2h_points + players_points + tactical_points + physical_points
            calculated_rating = total_points / 20  # Convert to 1-5 scale
            
            print(f"\nCalculated Total: {total_points:.1f}/100 pts → {calculated_rating:.2f}/5")
            print(f"Database Rating: {raw_data['final_rating']:.2f}/5")
            print(f"Match: {'✅' if abs(calculated_rating - raw_data['final_rating']) < 0.1 else '❌'}")
            
            # Add to manual data list
            manual_entry = {
                'opponent': raw_data['opponent_name'],
                'league_pos': raw_data['league_position'],
                'form_pts': raw_data['recent_form_points'],
                'venue': raw_data['venue'],
                'h2h': h2h_record,
                'h2h_score': f"{h2h_score:.3f}",
                'key_players': raw_data['key_players'],
                'tactical': f"{tactical_score:.3f}",
                'physical': f"{physical_score:.3f}",
                'expected_total': f"{total_points:.1f}",
                'expected_rating': f"{calculated_rating:.2f}"
            }
            manual_data.append(manual_entry)
        
        # Create summary table for Excel entry
        print(f"\n\n📋 SUMMARY TABLE FOR EXCEL ENTRY")
        print("=" * 120)
        print(f"{'Opponent':<15} {'Pos':<4} {'Form':<5} {'Venue':<5} {'H2H Score':<9} {'Players':<7} {'Tactical':<8} {'Physical':<8} {'Total':<6} {'Rating':<6}")
        print("-" * 120)
        
        for entry in manual_data:
            print(f"{entry['opponent']:<15} {entry['league_pos']:<4} {entry['form_pts']:<5} {entry['venue']:<5} {entry['h2h_score']:<9} {entry['key_players']:<7} {entry['tactical']:<8} {entry['physical']:<8} {entry['expected_total']:<6} {entry['expected_rating']:<6}")
        
        db.close()
        return manual_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    extract_opponent_data()
