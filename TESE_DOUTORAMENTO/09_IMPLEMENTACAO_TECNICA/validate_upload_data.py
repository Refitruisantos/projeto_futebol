#!/usr/bin/env python3
"""
Validate data before manual upload - check formats, constraints, and player names
"""
import sys
import pandas as pd
from pathlib import Path
import re

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

def get_database_players():
    """Get all active players from database"""
    try:
        db = DatabaseConnection()
        query = "SELECT nome_completo, jogador_id FROM atletas WHERE ativo = true"
        players = db.query_to_dict(query)
        db.close()
        
        player_names = set()
        for player in players:
            player_names.add(player['nome_completo'].strip().upper())
            if player['jogador_id']:
                player_names.add(player['jogador_id'].strip().upper())
        
        return player_names
    except Exception as e:
        print(f"❌ Error getting database players: {e}")
        return set()

def validate_gps_data(csv_file):
    """Validate GPS data file"""
    print(f"🔍 Validating GPS data: {csv_file}")
    
    if not Path(csv_file).exists():
        print(f"❌ File not found: {csv_file}")
        return False
    
    try:
        df = pd.read_csv(csv_file)
        print(f"📊 Found {len(df)} GPS records")
        
        # Check required columns
        required_columns = [
            'player', 'total_distance_m', 'max_velocity_kmh',
            'acc_b1_3_total_efforts', 'decel_b1_3_total_efforts',
            'efforts_over_19_8_kmh', 'distance_over_19_8_kmh',
            'efforts_over_25_2_kmh', 'velocity_b3_plus_total_efforts'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return False
        
        print("✅ All required columns present")
        
        # Validate data ranges
        errors = []
        
        for idx, row in df.iterrows():
            player_name = str(row['player']).strip()
            
            # Check distance (0-15000m reasonable range)
            distance = row['total_distance_m']
            if pd.isna(distance) or distance < 0 or distance > 15000:
                errors.append(f"Row {idx+1} ({player_name}): Invalid distance {distance}m")
            
            # Check max velocity (0-40 km/h reasonable range)
            velocity = row['max_velocity_kmh']
            if pd.isna(velocity) or velocity < 0 or velocity > 40:
                errors.append(f"Row {idx+1} ({player_name}): Invalid max velocity {velocity} km/h")
            
            # Check efforts (0-200 reasonable range)
            for effort_col in ['acc_b1_3_total_efforts', 'decel_b1_3_total_efforts', 
                              'efforts_over_19_8_kmh', 'efforts_over_25_2_kmh', 
                              'velocity_b3_plus_total_efforts']:
                effort_val = row[effort_col]
                if pd.isna(effort_val) or effort_val < 0 or effort_val > 200:
                    errors.append(f"Row {idx+1} ({player_name}): Invalid {effort_col} {effort_val}")
        
        if errors:
            print(f"❌ Found {len(errors)} data validation errors:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(errors) > 10:
                print(f"   ... and {len(errors) - 10} more errors")
            return False
        
        print("✅ All GPS data values within valid ranges")
        
        # Check player names against database
        db_players = get_database_players()
        if db_players:
            name_errors = []
            for idx, row in df.iterrows():
                player_name = str(row['player']).strip().upper()
                if player_name not in db_players:
                    name_errors.append(f"Row {idx+1}: Player '{row['player']}' not found in database")
            
            if name_errors:
                print(f"❌ Found {len(name_errors)} player name errors:")
                for error in name_errors[:5]:
                    print(f"   - {error}")
                print("\n💡 Available players in database:")
                for name in sorted(list(db_players)[:10]):
                    print(f"   - {name}")
                return False
            
            print("✅ All player names match database")
        
        print("🎉 GPS data validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error validating GPS data: {e}")
        return False

def validate_pse_data(csv_file):
    """Validate PSE/wellness data file"""
    print(f"🔍 Validating PSE data: {csv_file}")
    
    if not Path(csv_file).exists():
        print(f"❌ File not found: {csv_file}")
        return False
    
    try:
        df = pd.read_csv(csv_file)
        print(f"📊 Found {len(df)} PSE records")
        
        # Check required columns
        required_columns = ['Nome', 'Pos', 'Sono', 'Stress', 'Fadiga', 'DOMS', 'VOLUME', 'Rpe', 'CARGA']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return False
        
        print("✅ All required columns present")
        
        # Validate data ranges
        errors = []
        
        for idx, row in df.iterrows():
            player_name = str(row['Nome']).strip()
            
            # Check sleep quality (1-10)
            sono = row['Sono']
            if pd.isna(sono) or sono < 1 or sono > 10:
                errors.append(f"Row {idx+1} ({player_name}): Invalid sleep quality {sono} (must be 1-10)")
            
            # Check stress, fatigue, DOMS (1-5)
            for scale_col in ['Stress', 'Fadiga', 'DOMS']:
                val = row[scale_col]
                if pd.isna(val) or val < 1 or val > 5:
                    errors.append(f"Row {idx+1} ({player_name}): Invalid {scale_col} {val} (must be 1-5)")
            
            # Check RPE (1-10)
            rpe = row['Rpe']
            if pd.isna(rpe) or rpe < 1 or rpe > 10:
                errors.append(f"Row {idx+1} ({player_name}): Invalid RPE {rpe} (must be 1-10)")
            
            # Check volume (30-180 minutes reasonable)
            volume = row['VOLUME']
            if pd.isna(volume) or volume < 30 or volume > 180:
                errors.append(f"Row {idx+1} ({player_name}): Invalid volume {volume} minutes (30-180 expected)")
            
            # Check load (positive number)
            carga = row['CARGA']
            if pd.isna(carga) or carga <= 0:
                errors.append(f"Row {idx+1} ({player_name}): Invalid load {carga} (must be positive)")
            
            # Check position
            pos = str(row['Pos']).strip().upper()
            valid_positions = ['DC', 'MC', 'EX', 'AV', 'GR']
            if pos not in valid_positions:
                errors.append(f"Row {idx+1} ({player_name}): Invalid position '{pos}' (must be: {valid_positions})")
        
        if errors:
            print(f"❌ Found {len(errors)} data validation errors:")
            for error in errors[:10]:
                print(f"   - {error}")
            if len(errors) > 10:
                print(f"   ... and {len(errors) - 10} more errors")
            return False
        
        print("✅ All PSE data values within valid ranges")
        
        # Check player names against database
        db_players = get_database_players()
        if db_players:
            name_errors = []
            for idx, row in df.iterrows():
                player_name = str(row['Nome']).strip().upper()
                if player_name not in db_players:
                    name_errors.append(f"Row {idx+1}: Player '{row['Nome']}' not found in database")
            
            if name_errors:
                print(f"❌ Found {len(name_errors)} player name errors:")
                for error in name_errors[:5]:
                    print(f"   - {error}")
                return False
            
            print("✅ All player names match database")
        
        print("🎉 PSE data validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error validating PSE data: {e}")
        return False

def main():
    """Main validation function"""
    if len(sys.argv) < 2:
        print("Usage: python validate_upload_data.py <gps_file> [pse_file]")
        print("Example: python validate_upload_data.py gps_2025-03-15_training.csv pse_2025-03-15_training.csv")
        return
    
    gps_file = sys.argv[1]
    pse_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("🔍 Data Validation Tool")
    print("=" * 50)
    
    gps_valid = validate_gps_data(gps_file)
    
    pse_valid = True
    if pse_file:
        print("\n" + "-" * 50)
        pse_valid = validate_pse_data(pse_file)
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    if gps_valid:
        print("✅ GPS data: VALID - Ready for upload")
    else:
        print("❌ GPS data: INVALID - Fix errors before upload")
    
    if pse_file:
        if pse_valid:
            print("✅ PSE data: VALID - Ready for upload")
        else:
            print("❌ PSE data: INVALID - Fix errors before upload")
    
    if gps_valid and pse_valid:
        print("\n🎉 All data validated successfully!")
        print("📤 Ready for manual upload process")
    else:
        print("\n⚠️ Please fix validation errors before uploading")

if __name__ == "__main__":
    main()
