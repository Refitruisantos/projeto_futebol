"""
Test Mock Data Generation System

Simple script to test the mock data generation without needing the API
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'utils'))

from importlib.machinery import SourceFileLoader
db_module = SourceFileLoader('conexao_db', 'python/01_conexao_db.py').load_module()

try:
    from mock_data_generator import MockDataGenerator, GenerationConfig, ScenarioType
except ImportError as e:
    print(f"❌ Error importing mock_data_generator: {e}")
    print("\nTrying alternative import...")
    sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'utils'))
    from mock_data_generator import MockDataGenerator, GenerationConfig, ScenarioType


def test_basic_generation():
    """Test basic data generation"""
    print("=" * 80)
    print("TEST 1: Basic Generation (1 Week, 5 Athletes)")
    print("=" * 80)
    
    config = GenerationConfig(
        start_date=datetime(2025, 1, 6),  # Monday
        end_date=datetime(2025, 1, 12),   # Sunday
        num_athletes=5,
        positions=['GR', 'DC', 'MC', 'EX', 'AV'],
        training_days=[0, 1, 2, 3, 4],  # Mon-Fri
        game_days=[5],  # Saturday
        sessions_per_week=6,
        scenario=ScenarioType.NORMAL,
        seed=42
    )
    
    generator = MockDataGenerator(config)
    dataset = generator.generate_full_dataset()
    
    print(f"\n✅ Generated:")
    print(f"   Athletes: {len(dataset['athletes'])}")
    print(f"   Sessions: {len(dataset['sessions'])}")
    print(f"   PSE records: {len(dataset['pse_data'])}")
    print(f"   GPS records: {len(dataset['gps_data'])}")
    
    # Show sample athlete
    if dataset['athletes']:
        athlete = dataset['athletes'][0]
        print(f"\n📋 Sample Athlete:")
        print(f"   Name: {athlete['nome_completo']}")
        print(f"   Position: {athlete['posicao']}")
        print(f"   Height: {athlete['altura_cm']} cm")
        print(f"   Weight: {athlete['massa_kg']} kg")
    
    # Show sample PSE record
    if dataset['pse_data']:
        pse = dataset['pse_data'][0]
        print(f"\n📊 Sample PSE Record:")
        print(f"   Date: {pse['time']}")
        print(f"   PSE: {pse['pse']}")
        print(f"   Duration: {pse['duracao_min']} min")
        print(f"   Load: {pse['carga_total']}")
    
    # Calculate average load per athlete
    athlete_loads = {}
    for record in dataset['pse_data']:
        aid = record['atleta_id']
        if aid not in athlete_loads:
            athlete_loads[aid] = []
        athlete_loads[aid].append(record['carga_total'])
    
    print(f"\n📈 Weekly Load Summary:")
    for athlete in dataset['athletes']:
        aid = athlete['numero_camisola']
        loads = athlete_loads.get(aid, [])
        if loads:
            total = sum(loads)
            avg = total / len(loads)
            print(f"   {athlete['nome_completo']:20s} | Sessions: {len(loads)} | Total: {total:6.0f} | Avg: {avg:5.0f}")
    
    return dataset


def test_scenario_comparison():
    """Test different scenarios"""
    print("\n" + "=" * 80)
    print("TEST 2: Scenario Comparison (2 Weeks, Same Athletes)")
    print("=" * 80)
    
    scenarios = [
        ScenarioType.NORMAL,
        ScenarioType.TAPER,
        ScenarioType.OVERLOAD
    ]
    
    results = {}
    
    for scenario in scenarios:
        config = GenerationConfig(
            start_date=datetime(2025, 1, 6),
            end_date=datetime(2025, 1, 19),
            num_athletes=3,
            positions=['MC', 'MC', 'MC'],  # Same position for fair comparison
            training_days=[0, 1, 2, 3, 4],
            game_days=[5],
            sessions_per_week=6,
            scenario=scenario,
            seed=42
        )
        
        generator = MockDataGenerator(config)
        dataset = generator.generate_full_dataset()
        
        # Calculate average load
        total_load = sum(r['carga_total'] for r in dataset['pse_data'])
        avg_load = total_load / len(dataset['pse_data']) if dataset['pse_data'] else 0
        
        results[scenario.value] = {
            'total_load': total_load,
            'avg_load': avg_load,
            'sessions': len(dataset['sessions']),
            'pse_records': len(dataset['pse_data'])
        }
    
    print(f"\n{'Scenario':<20} | {'Avg Load':<10} | {'Total Load':<12} | {'Sessions'}")
    print("-" * 80)
    for scenario_name, stats in results.items():
        print(f"{scenario_name:<20} | {stats['avg_load']:>10.1f} | {stats['total_load']:>12.0f} | {stats['sessions']:>8}")
    
    print(f"\n💡 Expected:")
    print(f"   TAPER should have ~70% of NORMAL load")
    print(f"   OVERLOAD should have ~120% of NORMAL load")
    
    return results


def test_position_differences():
    """Test position-specific modifiers"""
    print("\n" + "=" * 80)
    print("TEST 3: Position-Specific Differences (1 Week Each)")
    print("=" * 80)
    
    positions = ['GR', 'DC', 'MC', 'EX', 'AV']
    results = {}
    
    for position in positions:
        config = GenerationConfig(
            start_date=datetime(2025, 1, 6),
            end_date=datetime(2025, 1, 12),
            num_athletes=1,
            positions=[position],
            training_days=[0, 1, 2, 3, 4],
            game_days=[5],
            sessions_per_week=6,
            scenario=ScenarioType.NORMAL,
            seed=42
        )
        
        generator = MockDataGenerator(config)
        dataset = generator.generate_full_dataset()
        
        # Calculate averages
        pse_records = dataset['pse_data']
        gps_records = dataset['gps_data']
        
        avg_load = sum(r['carga_total'] for r in pse_records) / len(pse_records) if pse_records else 0
        avg_distance = sum(r['distancia_total'] for r in gps_records) / len(gps_records) if gps_records else 0
        avg_sprints = sum(r['sprints'] for r in gps_records) / len(gps_records) if gps_records else 0
        
        results[position] = {
            'avg_load': avg_load,
            'avg_distance': avg_distance,
            'avg_sprints': avg_sprints
        }
    
    print(f"\n{'Position':<10} | {'Avg Load':<10} | {'Avg Distance':<14} | {'Avg Sprints'}")
    print("-" * 80)
    for pos, stats in results.items():
        print(f"{pos:<10} | {stats['avg_load']:>10.1f} | {stats['avg_distance']:>14.0f} | {stats['avg_sprints']:>11.1f}")
    
    print(f"\n💡 Expected:")
    print(f"   GR should have lowest load, distance, and sprints")
    print(f"   AV should have highest sprints")
    print(f"   MC should have highest distance")
    
    return results


def test_reproducibility():
    """Test that same seed produces same results"""
    print("\n" + "=" * 80)
    print("TEST 4: Reproducibility (Same Seed = Same Data)")
    print("=" * 80)
    
    config = GenerationConfig(
        start_date=datetime(2025, 1, 6),
        end_date=datetime(2025, 1, 12),
        num_athletes=3,
        positions=['MC', 'MC', 'MC'],
        training_days=[0, 1, 2, 3, 4],
        game_days=[5],
        sessions_per_week=6,
        scenario=ScenarioType.NORMAL,
        seed=123  # Fixed seed
    )
    
    # Generate twice
    gen1 = MockDataGenerator(config)
    dataset1 = gen1.generate_full_dataset()
    
    gen2 = MockDataGenerator(config)
    dataset2 = gen2.generate_full_dataset()
    
    # Compare first PSE record
    pse1 = dataset1['pse_data'][0]
    pse2 = dataset2['pse_data'][0]
    
    match = (
        pse1['pse'] == pse2['pse'] and
        pse1['duracao_min'] == pse2['duracao_min'] and
        pse1['carga_total'] == pse2['carga_total']
    )
    
    if match:
        print(f"\n✅ PASS: Same seed produces identical results")
        print(f"   First record PSE: {pse1['pse']}")
        print(f"   First record Duration: {pse1['duracao_min']}")
        print(f"   First record Load: {pse1['carga_total']}")
    else:
        print(f"\n❌ FAIL: Results differ despite same seed")
        print(f"   Gen1: PSE={pse1['pse']}, Dur={pse1['duracao_min']}, Load={pse1['carga_total']}")
        print(f"   Gen2: PSE={pse2['pse']}, Dur={pse2['duracao_min']}, Load={pse2['carga_total']}")
    
    return match


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("🧪 MOCK DATA GENERATION SYSTEM - TEST SUITE")
    print("=" * 80)
    print()
    
    try:
        # Test 1: Basic generation
        test_basic_generation()
        
        # Test 2: Scenario comparison
        test_scenario_comparison()
        
        # Test 3: Position differences
        test_position_differences()
        
        # Test 4: Reproducibility
        reproducible = test_reproducibility()
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)
        print(f"\n🎯 System Status: OPERATIONAL")
        print(f"   Reproducibility: {'✅ PASS' if reproducible else '❌ FAIL'}")
        print(f"\nNext steps:")
        print(f"  1. Generate larger dataset (1+ months)")
        print(f"  2. Process through calculate_weekly_metrics.py")
        print(f"  3. Use for model training/testing")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
