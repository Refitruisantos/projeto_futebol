#!/usr/bin/env python3
"""
Generate all GPS and PSE files for Jornada 25 and 26 complete rounds
"""
import csv
import random
from pathlib import Path

def generate_gps_data(session_type, intensity_level):
    """Generate GPS data based on session type and intensity"""
    base_distances = {
        'recovery': (4500, 5500),
        'technical': (6500, 7500),
        'tactical': (7500, 8500),
        'physical': (8500, 9500),
        'prematch': (5500, 6500),
        'match': (9500, 11500)
    }
    
    base_speeds = {
        'recovery': (22, 25),
        'technical': (26, 28),
        'tactical': (28, 30),
        'physical': (29, 32),
        'prematch': (25, 27),
        'match': (30, 33)
    }
    
    players = [
        "Tiago Silva", "Diogo Martins", "Carlos Oliveira", "Tiago Ribeiro", "Miguel Pinto",
        "Bruno Santos", "Francisco Costa", "João Pereira", "André Ferreira", "Pedro Almeida",
        "Rafael Sousa", "Gonçalo Lima", "Nuno Rodrigues", "Luís Carvalho", "Manuel Dias",
        "José Mendes", "Paulo Gomes", "Rúben Lopes", "Daniel Neves", "Marco Teixeira"
    ]
    
    dist_min, dist_max = base_distances[session_type]
    speed_min, speed_max = base_speeds[session_type]
    
    data = []
    for player in players:
        # Adjust for goalkeeper (Paulo Gomes)
        if player == "Paulo Gomes":
            distance = random.uniform(dist_min * 0.7, dist_max * 0.7)
            max_speed = random.uniform(speed_min * 0.8, speed_max * 0.8)
            efforts_multiplier = 0.6
        else:
            distance = random.uniform(dist_min, dist_max)
            max_speed = random.uniform(speed_min, speed_max)
            efforts_multiplier = 1.0
        
        # Calculate efforts based on intensity
        base_acc = int(random.uniform(25, 55) * efforts_multiplier * intensity_level)
        base_decel = int(random.uniform(20, 50) * efforts_multiplier * intensity_level)
        high_efforts = int(random.uniform(5, 20) * efforts_multiplier * intensity_level)
        high_distance = random.uniform(100, 350) * intensity_level
        very_high_efforts = int(random.uniform(1, 8) * efforts_multiplier * intensity_level)
        velocity_efforts = int(random.uniform(25, 60) * efforts_multiplier * intensity_level)
        
        data.append([
            player, f"{distance:.1f}", f"{max_speed:.1f}",
            base_acc, base_decel, high_efforts, f"{high_distance:.1f}",
            very_high_efforts, velocity_efforts
        ])
    
    return data

def generate_pse_data(session_type, day_in_cycle):
    """Generate PSE data based on session type and position in training cycle"""
    rpe_ranges = {
        'recovery': (3, 5),
        'technical': (5, 7),
        'tactical': (6, 8),
        'physical': (7, 9),
        'prematch': (4, 6),
        'match': (8, 10)
    }
    
    durations = {
        'recovery': 75,
        'technical': 90,
        'tactical': 105,
        'physical': 120,
        'prematch': 60,
        'match': 95
    }
    
    players_positions = [
        ("Tiago Silva", "DC"), ("Diogo Martins", "DC"), ("Carlos Oliveira", "MC"), 
        ("Tiago Ribeiro", "MC"), ("Miguel Pinto", "MC"), ("Bruno Santos", "EX"),
        ("Francisco Costa", "EX"), ("João Pereira", "EX"), ("André Ferreira", "MC"),
        ("Pedro Almeida", "AV"), ("Rafael Sousa", "AV"), ("Gonçalo Lima", "DC"),
        ("Nuno Rodrigues", "MC"), ("Luís Carvalho", "EX"), ("Manuel Dias", "AV"),
        ("José Mendes", "AV"), ("Paulo Gomes", "GR"), ("Rúben Lopes", "DC"),
        ("Daniel Neves", "MC"), ("Marco Teixeira", "EX")
    ]
    
    rpe_min, rpe_max = rpe_ranges[session_type]
    duration = durations[session_type]
    
    # Fatigue accumulation based on day in cycle
    fatigue_modifier = min(day_in_cycle * 0.3, 2.0)
    
    data = []
    for player, position in players_positions:
        # Individual variation
        individual_factor = random.uniform(0.8, 1.2)
        
        # Sleep quality (decreases with fatigue)
        sleep = max(1, min(10, int(random.uniform(6, 9) - fatigue_modifier)))
        
        # Stress (increases with intensity and fatigue)
        stress = max(1, min(5, int(random.uniform(2, 4) + (rpe_min / 3) + (fatigue_modifier * 0.5))))
        
        # Fatigue (increases through cycle)
        fatigue = max(1, min(5, int(random.uniform(2, 4) + fatigue_modifier)))
        
        # DOMS (related to previous day intensity)
        doms = max(1, min(5, int(random.uniform(1, 3) + fatigue_modifier * 0.7)))
        
        # Muscle pain (similar to DOMS)
        muscle_pain = max(1, min(5, int(random.uniform(1, 3) + fatigue_modifier * 0.6)))
        
        # RPE with individual variation
        rpe = max(1, min(10, int(random.uniform(rpe_min, rpe_max) * individual_factor)))
        
        # Load calculation
        load = duration * rpe
        
        data.append([
            player, position, sleep, stress, fatigue, doms, muscle_pain,
            duration, rpe, load
        ])
    
    return data

def create_round_files(jornada_num, start_date_str):
    """Create all files for a complete round"""
    
    sessions = [
        ('recovery', 0.6, 'Recovery Training'),
        ('technical', 0.8, 'Technical Training'),
        ('tactical', 0.9, 'Tactical Training'),
        ('physical', 1.0, 'Physical Training'),
        ('prematch', 0.7, 'Pre-Match Activation'),
        ('match', 1.2, 'Match Day'),
        ('recovery', 0.5, 'Post-Match Recovery')
    ]
    
    rounds_dir = Path("rounds")
    rounds_dir.mkdir(exist_ok=True)
    
    for day, (session_type, intensity, description) in enumerate(sessions, 1):
        # Generate GPS data
        gps_data = generate_gps_data(session_type, intensity)
        gps_filename = f"jornada{jornada_num}_day{day}_{session_type}.csv"
        
        with open(rounds_dir / gps_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'player', 'total_distance_m', 'max_velocity_kmh',
                'acc_b1_3_total_efforts', 'decel_b1_3_total_efforts',
                'efforts_over_19_8_kmh', 'distance_over_19_8_kmh',
                'efforts_over_25_2_kmh', 'velocity_b3_plus_total_efforts'
            ])
            writer.writerows(gps_data)
        
        # Generate PSE data
        pse_data = generate_pse_data(session_type, day)
        pse_filename = f"jornada{jornada_num}_day{day}_pse.csv"
        
        with open(rounds_dir / pse_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Nome', 'Pos', 'Sono', 'Stress', 'Fadiga', 'DOMS',
                'DORES MUSCULARES', 'VOLUME', 'Rpe', 'CARGA'
            ])
            writer.writerows(pse_data)
        
        print(f"✅ Created {gps_filename} and {pse_filename}")

def main():
    """Generate all files for both complete rounds"""
    print("🏆 Generating Complete Rounds for Manual Upload")
    print("=" * 50)
    
    # Create Jornada 25 (March 24-30, 2025)
    print("\n📅 Creating Jornada 25 (March 24-30, 2025)")
    create_round_files(25, "2025-03-24")
    
    # Create Jornada 26 (March 31 - April 6, 2025)
    print("\n📅 Creating Jornada 26 (March 31 - April 6, 2025)")
    create_round_files(26, "2025-03-31")
    
    print("\n🎉 All files created successfully!")
    print("📊 Total files: 28 (14 GPS + 14 PSE)")
    print("📁 Location: rounds/ directory")
    print("\n🔄 Ready for manual upload practice!")

if __name__ == "__main__":
    main()
