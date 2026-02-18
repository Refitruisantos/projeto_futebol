"""
Clean PSE Long Format Data
===========================

Fixes common data quality issues before database import:
1. Fill missing RPE values
2. Fix DOMS=0 to valid range (1-5)
3. Calculate missing Carga values
4. Report missing athletes

Usage:
------
python scripts/clean_pse_data.py input.csv output_clean.csv
"""

import pandas as pd
import sys
from pathlib import Path


def clean_pse_data(input_csv: str, output_csv: str = None):
    """
    Clean PSE data for database import.
    
    Parameters:
    -----------
    input_csv : str
        Path to input CSV file
    output_csv : str, optional
        Path to output cleaned CSV. If None, overwrites input.
    """
    input_path = Path(input_csv)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    print(f"\n📂 Reading: {input_path.name}")
    
    # Read CSV
    df = pd.read_csv(input_path)
    
    print(f"   Original shape: {df.shape[0]} rows × {df.shape[1]} columns")
    
    original_count = len(df)
    
    # Track changes
    changes = {
        'missing_rpe_filled': 0,
        'doms_zero_fixed': 0,
        'doms_invalid_fixed': 0,
        'carga_calculated': 0,
        'rows_removed': 0
    }
    
    print(f"\n🔧 Cleaning data...")
    
    # 1. Handle missing RPE values
    print(f"\n1️⃣ Handling missing RPE values...")
    missing_rpe = df['RPE'].isna()
    
    if missing_rpe.any():
        print(f"   Found {missing_rpe.sum()} records with missing RPE")
        
        # Strategy A: If Volume and Carga exist, calculate RPE
        has_volume_carga = df['Volume'].notna() & df['Carga'].notna() & (df['Volume'] > 0)
        can_calculate = missing_rpe & has_volume_carga
        
        if can_calculate.any():
            df.loc[can_calculate, 'RPE'] = (df.loc[can_calculate, 'Carga'] / df.loc[can_calculate, 'Volume']).round()
            changes['missing_rpe_filled'] += can_calculate.sum()
            print(f"   ✓ Calculated RPE from Carga/Volume for {can_calculate.sum()} records")
        
        # Strategy B: If wellness data exists but no load data, use average wellness as proxy
        has_wellness = df[['Sono', 'Stress', 'Fadiga', 'DOMS']].notna().any(axis=1)
        wellness_only = missing_rpe & has_wellness & ~can_calculate
        
        if wellness_only.any():
            # Use moderate RPE value (5) as default for wellness-only records
            df.loc[wellness_only, 'RPE'] = 5
            df.loc[wellness_only, 'Volume'] = df.loc[wellness_only, 'Volume'].fillna(0)
            df.loc[wellness_only, 'Carga'] = 0
            changes['missing_rpe_filled'] += wellness_only.sum()
            print(f"   ✓ Set default RPE=5 for {wellness_only.sum()} wellness-only records")
        
        # Strategy C: Remove rows with no useful data at all
        no_data = missing_rpe & ~can_calculate & ~wellness_only
        if no_data.any():
            print(f"   ⚠️ Removing {no_data.sum()} rows with no useful data")
            df = df[~no_data]
            changes['rows_removed'] += no_data.sum()
    else:
        print(f"   ✓ All records have RPE values")
    
    # 2. Fix DOMS = 0 (should be 1-5)
    print(f"\n2️⃣ Fixing DOMS values...")
    doms_zero = (df['DOMS'] == 0)
    
    if doms_zero.any():
        print(f"   Found {doms_zero.sum()} records with DOMS=0")
        df.loc[doms_zero, 'DOMS'] = 1  # Convert 0 to 1 (minimum soreness)
        changes['doms_zero_fixed'] += doms_zero.sum()
        print(f"   ✓ Changed DOMS=0 to DOMS=1 for {doms_zero.sum()} records")
    
    # Check for other invalid DOMS values
    invalid_doms = (df['DOMS'].notna()) & ((df['DOMS'] < 1) | (df['DOMS'] > 5))
    
    if invalid_doms.any():
        print(f"   Found {invalid_doms.sum()} records with invalid DOMS (<1 or >5)")
        # Clip to valid range
        df.loc[invalid_doms & (df['DOMS'] < 1), 'DOMS'] = 1
        df.loc[invalid_doms & (df['DOMS'] > 5), 'DOMS'] = 5
        changes['doms_invalid_fixed'] += invalid_doms.sum()
        print(f"   ✓ Clipped DOMS to valid range (1-5)")
    
    if not doms_zero.any() and not invalid_doms.any():
        print(f"   ✓ All DOMS values are valid")
    
    # 3. Check and fix other wellness metrics
    print(f"\n3️⃣ Checking other wellness metrics...")
    wellness_cols = ['Sono', 'Stress', 'Fadiga']
    
    for col in wellness_cols:
        invalid = (df[col].notna()) & ((df[col] < 1) | (df[col] > 5))
        if invalid.any():
            print(f"   Found {invalid.sum()} records with invalid {col}")
            df.loc[invalid & (df[col] < 1), col] = 1
            df.loc[invalid & (df[col] > 5), col] = 5
            print(f"   ✓ Clipped {col} to valid range (1-5)")
    
    # 4. Calculate missing Carga values
    print(f"\n4️⃣ Calculating missing training load...")
    missing_carga = df['Carga'].isna() | (df['Carga'] == 0)
    can_calc_carga = missing_carga & df['RPE'].notna() & df['Volume'].notna()
    
    if can_calc_carga.any():
        df.loc[can_calc_carga, 'Carga'] = df.loc[can_calc_carga, 'RPE'] * df.loc[can_calc_carga, 'Volume']
        changes['carga_calculated'] += can_calc_carga.sum()
        print(f"   ✓ Calculated Carga for {can_calc_carga.sum()} records")
    else:
        print(f"   ✓ All records have Carga values")
    
    # 5. Identify missing athletes
    print(f"\n5️⃣ Checking for athletes not in database...")
    unique_athletes = sorted(df['Athlete'].unique())
    print(f"   Found {len(unique_athletes)} unique athletes:")
    
    # Common athletes that might be missing
    likely_missing = []
    for athlete in unique_athletes:
        # Check for single-letter or very short names (likely aggregate rows)
        if len(athlete) <= 2:
            likely_missing.append(athlete)
    
    if likely_missing:
        print(f"   ⚠️ Suspicious athlete names (likely aggregate rows):")
        for athlete in likely_missing:
            count = (df['Athlete'] == athlete).sum()
            print(f"      • {athlete}: {count} records")
        print(f"   → Consider removing these records")
    
    # Determine output path
    if output_csv is None:
        output_path = input_path.parent / f"{input_path.stem}_cleaned.csv"
    else:
        output_path = Path(output_csv)
    
    # Save cleaned data
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"\n{'='*60}")
    print(f"✅ CLEANING COMPLETE")
    print(f"{'='*60}")
    print(f"   Original records: {original_count}")
    print(f"   Cleaned records: {len(df)}")
    print(f"   Rows removed: {changes['rows_removed']}")
    print(f"\n📊 Changes made:")
    print(f"   • Missing RPE filled: {changes['missing_rpe_filled']}")
    print(f"   • DOMS=0 fixed: {changes['doms_zero_fixed']}")
    print(f"   • Invalid DOMS fixed: {changes['doms_invalid_fixed']}")
    print(f"   • Carga calculated: {changes['carga_calculated']}")
    
    print(f"\n✅ Saved: {output_path}")
    print(f"   Ready for import!")
    
    # Show data quality stats
    print(f"\n📈 Final data quality:")
    for col in ['RPE', 'Volume', 'Carga', 'Sono', 'Stress', 'Fadiga', 'DOMS']:
        if col in df.columns:
            non_null = df[col].notna().sum()
            pct = (non_null / len(df)) * 100
            print(f"   {col}: {non_null}/{len(df)} ({pct:.1f}%)")
    
    # Show unique athletes for database check
    print(f"\n👥 Unique athletes ({len(unique_athletes)}):")
    for athlete in unique_athletes[:20]:  # Show first 20
        print(f"   • {athlete}")
    if len(unique_athletes) > 20:
        print(f"   ... and {len(unique_athletes) - 20} more")
    
    return df, output_path


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Clean PSE data for database import.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('input_csv',
                       help='Input CSV file to clean')
    parser.add_argument('output_csv', nargs='?', default=None,
                       help='Output CSV file (optional, default: input_cleaned.csv)')
    
    args = parser.parse_args()
    
    try:
        clean_pse_data(args.input_csv, args.output_csv)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
