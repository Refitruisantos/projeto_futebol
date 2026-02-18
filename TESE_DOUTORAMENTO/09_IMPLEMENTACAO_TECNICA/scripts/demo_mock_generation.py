"""
Practical Demo: Generate Mock Data and Show Real Usage

Demonstrates the complete workflow:
1. Generate realistic training data
2. Export to CSV for inspection
3. Show statistics and patterns
4. Demonstrate how to use for ML/forecasting
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import csv
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'utils'))

from mock_data_generator import MockDataGenerator, GenerationConfig, ScenarioType

def main():
    print("=" * 80)
    print("🚀 PRACTICAL DEMO: Mock Data Generation for Forecasting")
    print("=" * 80)
    
    # Configuration: 1 month of realistic training data
    config = GenerationConfig(
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 31),
        num_athletes=20,
        positions=['GR', 'DC', 'DC', 'DL', 'DL', 'MC', 'MC', 'MC', 'EX', 'EX', 'AV', 'AV',
                   'GR', 'DC', 'DL', 'MC', 'EX', 'AV', 'MC', 'DC'],  # Realistic squad
        training_days=[0, 1, 2, 3, 4],  # Mon-Fri
        game_days=[5],  # Saturday
        sessions_per_week=6,
        scenario=ScenarioType.NORMAL,
        fidelity=0.85,  # High realism
        seed=42
    )
    
    print(f"\n📋 Configuration:")
    print(f"   Period: {config.start_date.date()} to {config.end_date.date()}")
    print(f"   Athletes: {config.num_athletes}")
    print(f"   Scenario: {config.scenario.value}")
    print(f"   Seed: {config.seed} (reproducible)")
    
    # Generate data
    print(f"\n⚙️  Generating data...")
    generator = MockDataGenerator(config)
    dataset = generator.generate_full_dataset()
    
    print(f"   ✅ Generated:")
    print(f"      Athletes: {len(dataset['athletes'])}")
    print(f"      Sessions: {len(dataset['sessions'])}")
    print(f"      PSE records: {len(dataset['pse_data'])}")
    print(f"      GPS records: {len(dataset['gps_data'])}")
    
    # Statistics
    print(f"\n📊 Data Statistics:")
    
    # Load statistics
    loads = [r['carga_total'] for r in dataset['pse_data']]
    avg_load = sum(loads) / len(loads)
    max_load = max(loads)
    min_load = min(loads)
    
    print(f"   Load (PSE × Duration):")
    print(f"      Mean: {avg_load:.1f}")
    print(f"      Min: {min_load:.1f}")
    print(f"      Max: {max_load:.1f}")
    
    # By session type
    session_types = {}
    for session in dataset['sessions']:
        tipo = session['tipo']
        session_types[tipo] = session_types.get(tipo, 0) + 1
    
    print(f"   Session Types:")
    for tipo, count in session_types.items():
        pct = (count / len(dataset['sessions'])) * 100
        print(f"      {tipo}: {count} sessions ({pct:.1f}%)")
    
    # By position
    print(f"\n📍 Average Load by Position:")
    position_loads = {}
    position_counts = {}
    
    for athlete in dataset['athletes']:
        pos = athlete['posicao']
        aid = athlete['numero_camisola']
        
        athlete_loads = [r['carga_total'] for r in dataset['pse_data'] if r['atleta_id'] == aid]
        
        if athlete_loads:
            avg = sum(athlete_loads) / len(athlete_loads)
            if pos not in position_loads:
                position_loads[pos] = []
            position_loads[pos].append(avg)
    
    for pos in ['GR', 'DC', 'DL', 'MC', 'EX', 'AV']:
        if pos in position_loads:
            avg = sum(position_loads[pos]) / len(position_loads[pos])
            print(f"      {pos}: {avg:.1f}")
    
    # Export to CSV
    print(f"\n💾 Exporting data...")
    
    # Export PSE data
    pse_file = 'mock_pse_january_2025.csv'
    with open(pse_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['time', 'atleta_id', 'sessao_id', 'pse', 'duracao_min', 'carga_total'])
        writer.writeheader()
        writer.writerows(dataset['pse_data'])
    print(f"   ✅ PSE data: {pse_file}")
    
    # Export GPS data
    if dataset['gps_data']:
        gps_file = 'mock_gps_january_2025.csv'
        with open(gps_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['time', 'atleta_id', 'sessao_id', 'distancia_total', 'velocidade_max', 
                         'velocidade_media', 'sprints', 'aceleracoes', 'desaceleracoes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(dataset['gps_data'])
        print(f"   ✅ GPS data: {gps_file}")
    
    # Export athletes
    athletes_file = 'mock_athletes.csv'
    with open(athletes_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['jogador_id', 'nome_completo', 'data_nascimento', 'posicao', 
                     'numero_camisola', 'altura_cm', 'massa_kg', 'pe_dominante', 'ativo']
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(dataset['athletes'])
    print(f"   ✅ Athletes: {athletes_file}")
    
    # Export sessions
    sessions_file = 'mock_sessions.csv'
    with open(sessions_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'data', 'hora_inicio', 'tipo', 'duracao_min'])
        writer.writeheader()
        writer.writerows(dataset['sessions'])
    print(f"   ✅ Sessions: {sessions_file}")
    
    # Show sample weekly pattern for one athlete
    print(f"\n📅 Sample: Weekly Pattern for One Athlete")
    sample_athlete = dataset['athletes'][5]  # Mid-field player
    athlete_id = sample_athlete['numero_camisola']
    
    print(f"   Athlete: {sample_athlete['nome_completo']} ({sample_athlete['posicao']})")
    print(f"   Week 1 (Jan 6-12):")
    
    week1_data = [r for r in dataset['pse_data'] 
                  if r['atleta_id'] == athlete_id 
                  and datetime(2025, 1, 6) <= r['time'] <= datetime(2025, 1, 12)]
    
    for record in sorted(week1_data, key=lambda x: x['time']):
        day_name = record['time'].strftime('%A')
        print(f"      {day_name:10s} | PSE: {record['pse']:4.1f} | Duration: {record['duracao_min']:3d} min | Load: {record['carga_total']:6.1f}")
    
    week_total = sum(r['carga_total'] for r in week1_data)
    print(f"      {'Total':10s} | Weekly Load: {week_total:.0f}")
    
    # Usage examples
    print(f"\n" + "=" * 80)
    print(f"✅ GENERATION COMPLETE")
    print(f"=" * 80)
    
    print(f"\n💡 Next Steps - How to Use This Data:")
    print(f"\n1️⃣  Inspect the generated files:")
    print(f"   > import pandas as pd")
    print(f"   > df = pd.read_csv('{pse_file}')")
    print(f"   > df.head()")
    
    print(f"\n2️⃣  Process through metrics pipeline:")
    print(f"   > python scripts/calculate_weekly_metrics.py")
    print(f"   (after importing mock data to database)")
    
    print(f"\n3️⃣  Train forecasting model:")
    print(f"   > # Load data")
    print(f"   > df = pd.read_csv('{pse_file}')")
    print(f"   > df['time'] = pd.to_datetime(df['time'])")
    print(f"   >")
    print(f"   > # Train LSTM/ARIMA/etc.")
    print(f"   > model.fit(df)")
    print(f"   > predictions = model.predict(future_dates)")
    
    print(f"\n4️⃣  Backtesting:")
    print(f"   > # Generate multiple scenarios")
    print(f"   > for seed in range(10):")
    print(f"   >     dataset = generate(seed=seed)")
    print(f"   >     evaluate_model(dataset)")
    
    print(f"\n5️⃣  Scenario comparison:")
    print(f"   > scenarios = ['normal', 'taper', 'overload', 'game_congestion']")
    print(f"   > for scenario in scenarios:")
    print(f"   >     test_model_on_scenario(scenario)")
    
    print(f"\n📄 Files created in current directory:")
    print(f"   - {pse_file}")
    print(f"   - {gps_file}")
    print(f"   - {athletes_file}")
    print(f"   - {sessions_file}")
    
    print(f"\n🎯 System ready for ML model testing and forecasting!")
    print("=" * 80)

if __name__ == '__main__':
    main()
