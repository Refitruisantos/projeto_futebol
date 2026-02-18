"""
Transform PSE Wide Format to Long Format
=========================================

Specialized script for transforming complex PSE CSV files where each athlete
has multiple sessions spread across columns in a single row.

Input Structure (Wide Format):
------------------------------
Row 1: Headers (Nome repeated, then session types)
Row 2: Subheaders (Pos, Sono, Stress, Fadiga, DOMS, VOLUME, Rpe, CARGA repeated)
Row 3+: Athlete data with values for each session

Example Input:
Nome;;;;; | Nome;;;;; | Nome;;;;;
;Pos;Sono;Stress;Fadiga;DOMS;VOLUME;Rpe;CARGA | ;Pos;Sono;Stress;Fadiga;DOMS;VOLUME;Rpe;CARGA
ANDRADE;LAT;8;8;3;3;90;4;360 | ANDRADE;LAT;8;8;3;3;90;7;630

Output Structure (Long Format):
-------------------------------
Athlete,Session,Posicao,Sono,Stress,Fadiga,DOMS,Volume,RPE,Carga
ANDRADE,1,LAT,8,8,3,3,90,4,360
ANDRADE,2,LAT,8,8,3,3,90,7,630

Usage:
------
python scripts/transform_pse_wide_to_long.py Jogo1_pse.csv
"""

import pandas as pd
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import re


def parse_pse_wide_format(csv_path: str, output_path: str = None) -> pd.DataFrame:
    """
    Parse complex PSE CSV with multiple sessions per athlete row.
    
    Parameters:
    -----------
    csv_path : str
        Path to input PSE CSV file
    output_path : str, optional
        Path to output CSV. If None, uses input_name_long.csv
    
    Returns:
    --------
    pd.DataFrame
        Long format DataFrame
    """
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Input file not found: {csv_path}")
    
    print(f"\n📂 Reading: {csv_path.name}")
    
    # Read CSV with semicolon separator (PSE files use semicolons)
    df = pd.read_csv(csv_path, sep=';', header=None, encoding='utf-8')
    
    print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Skip first 2 header rows
    data_rows = df.iloc[2:].copy()
    
    # Identify session blocks
    # Pattern: Nome, Pos, Sono, Stress, Fadiga, DOMS, DORES, Empty, VOLUME, Rpe, CARGA, Empty
    # Structure: 12 columns per session (athlete name repeats at start of each block)
    columns_per_session = 12
    
    # Calculate number of sessions (excluding summary columns at end)
    # Count by checking for athlete names in column 0, 12, 24, etc.
    num_sessions = 0
    for col_idx in range(0, df.shape[1], columns_per_session):
        # Check if this looks like a session block (has athlete names in data rows)
        if col_idx + 10 < df.shape[1]:  # Need at least 11 columns for a session
            # Check a few data rows to see if they have athlete names
            has_names = False
            for check_row in range(2, min(7, len(df))):
                val = df.iloc[check_row, col_idx]
                if pd.notna(val) and isinstance(val, str) and len(val) > 2:
                    has_names = True
                    break
            if has_names:
                num_sessions += 1
            else:
                break  # Stop when we hit summary columns
        else:
            break
    
    print(f"   Detected {num_sessions} session blocks")
    
    # Collect long format data
    long_data = []
    
    for idx, row in data_rows.iterrows():
        # Extract athlete name from first column
        athlete_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None
        
        if not athlete_name or athlete_name == '' or athlete_name == 'nan':
            continue
        
        # Process each session block
        for session_num in range(num_sessions):
            base_col = session_num * columns_per_session
            
            # Verify we have enough columns
            if base_col + 10 >= len(row):
                continue
            
            # Extract session data from correct column offsets
            # Block structure (12 columns): Nome(0), Pos(1), Sono(2), Stress(3), Fadiga(4), DOMS(5), 
            #                               DORES(6), Empty(7), VOLUME(8), Rpe(9), CARGA(10), Empty(11)
            
            posicao = row.iloc[base_col + 1] if base_col + 1 < len(row) and pd.notna(row.iloc[base_col + 1]) else None
            sono = row.iloc[base_col + 2] if base_col + 2 < len(row) and pd.notna(row.iloc[base_col + 2]) else None
            stress = row.iloc[base_col + 3] if base_col + 3 < len(row) and pd.notna(row.iloc[base_col + 3]) else None
            fadiga = row.iloc[base_col + 4] if base_col + 4 < len(row) and pd.notna(row.iloc[base_col + 4]) else None
            doms = row.iloc[base_col + 5] if base_col + 5 < len(row) and pd.notna(row.iloc[base_col + 5]) else None
            volume = row.iloc[base_col + 8] if base_col + 8 < len(row) and pd.notna(row.iloc[base_col + 8]) else None
            rpe = row.iloc[base_col + 9] if base_col + 9 < len(row) and pd.notna(row.iloc[base_col + 9]) else None
            carga = row.iloc[base_col + 10] if base_col + 10 < len(row) and pd.notna(row.iloc[base_col + 10]) else None
            
            # Skip sessions with no data (all None)
            if all(pd.isna(v) or v == '' for v in [sono, stress, fadiga, doms, volume, rpe, carga]):
                continue
            
            # Helper function to safely convert to int
            def safe_int(value):
                if pd.isna(value) or str(value).strip() == '':
                    return None
                try:
                    return int(float(value))  # float first to handle decimals
                except (ValueError, TypeError):
                    return None
            
            # Validate position field - should be standard position codes
            valid_positions = ['GR', 'DC', 'DL', 'DD', 'LAT', 'MED', 'MC', 'EXT', 'AV', 'PL']
            position_str = str(posicao).strip().upper() if pd.notna(posicao) else None
            
            # Skip if position is athlete name (indicates aggregate row)
            if position_str and position_str == athlete_name.upper():
                continue
            
            # Skip if position is numeric (indicates aggregate row)
            if position_str:
                try:
                    float(position_str.replace(',', '.'))
                    continue  # It's a number, skip this row
                except (ValueError, AttributeError):
                    pass  # Not a number, proceed
            
            # Skip if position contains invalid characters (aggregate rows often have text)
            if position_str and any(char in position_str for char in ['/', 'MÉDIA', 'CARGA', 'COM', 'VALORES']):
                continue
            
            # Clean position to standard codes
            if position_str and position_str not in valid_positions:
                # Map common variations
                pos_map = {
                    'MEDIO': 'MED',
                    'MÉDIO': 'MED',
                    'LATERAL': 'LAT',
                    'DEFESA': 'DC',
                    'AVANÇADO': 'AV',
                    'EXTREMO': 'EXT'
                }
                position_str = pos_map.get(position_str, position_str)
            
            # Create session record
            session_record = {
                'Athlete': athlete_name,
                'Session': session_num + 1,  # 1-indexed
                'Posicao': position_str if position_str in valid_positions else None,
                'Sono': safe_int(sono),
                'Stress': safe_int(stress),
                'Fadiga': safe_int(fadiga),
                'DOMS': safe_int(doms),
                'Volume': safe_int(volume),
                'RPE': safe_int(rpe),
                'Carga': safe_int(carga)
            }
            
            long_data.append(session_record)
    
    # Create long format DataFrame
    df_long = pd.DataFrame(long_data)
    
    # Sort by Athlete, Session
    df_long = df_long.sort_values(['Athlete', 'Session']).reset_index(drop=True)
    
    print(f"✓ Transformed to {len(df_long)} records")
    
    # Determine output path
    if output_path is None:
        output_path = csv_path.parent / f"{csv_path.stem}_long.csv"
    else:
        output_path = Path(output_path)
    
    # Save output
    df_long.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\n✅ Saved: {output_path}")
    
    # Show preview
    print(f"\n📊 Preview (first 15 rows):")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 120)
    print(df_long.head(15).to_string(index=False))
    
    # Show statistics
    print(f"\n📈 Statistics:")
    print(f"   Unique athletes: {df_long['Athlete'].nunique()}")
    print(f"   Total records: {len(df_long)}")
    print(f"   Sessions per athlete (avg): {len(df_long) / df_long['Athlete'].nunique():.1f}")
    
    # Check for missing values
    wellness_cols = ['Sono', 'Stress', 'Fadiga', 'DOMS']
    load_cols = ['Volume', 'RPE', 'Carga']
    
    print(f"\n📋 Data completeness:")
    for col in wellness_cols + load_cols:
        non_null = df_long[col].notna().sum()
        pct = (non_null / len(df_long)) * 100
        print(f"   {col}: {non_null}/{len(df_long)} ({pct:.1f}%)")
    
    # Position distribution
    if df_long['Posicao'].notna().any():
        print(f"\n👥 Position distribution:")
        pos_counts = df_long['Posicao'].value_counts()
        for pos, count in pos_counts.items():
            print(f"   {pos}: {count}")
    
    return df_long


def transform_all_pse_files(input_dir: str, output_dir: str = None):
    """
    Transform all PSE files in a directory.
    
    Parameters:
    -----------
    input_dir : str
        Directory containing PSE CSV files
    output_dir : str, optional
        Output directory for transformed files. If None, uses input_dir
    """
    input_dir = Path(input_dir)
    
    if not input_dir.exists():
        raise FileNotFoundError(f"Directory not found: {input_dir}")
    
    # Find all PSE CSV files
    pse_files = sorted(input_dir.glob('*pse.csv'))
    
    if not pse_files:
        print(f"⚠️ No PSE CSV files found in {input_dir}")
        return
    
    print(f"\n🔄 Found {len(pse_files)} PSE files to transform:")
    for f in pse_files:
        print(f"   • {f.name}")
    
    print("\n" + "="*80)
    
    # Transform each file
    all_data = []
    
    for pse_file in pse_files:
        print(f"\n{'='*80}")
        print(f"Processing: {pse_file.name}")
        print(f"{'='*80}")
        
        try:
            # Determine output path
            if output_dir:
                output_path = Path(output_dir) / f"{pse_file.stem}_long.csv"
            else:
                output_path = None  # Will use input dir with _long suffix
            
            df = parse_pse_wide_format(pse_file, output_path)
            
            # Add jornada identifier from filename
            jornada_match = re.search(r'jogo(\d+)', pse_file.name.lower())
            if jornada_match:
                jornada_num = int(jornada_match.group(1))
                df['Jornada'] = jornada_num
                all_data.append(df)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    # Combine all jornadas into one file
    if all_data:
        print(f"\n{'='*80}")
        print(f"COMBINING ALL JORNADAS")
        print(f"{'='*80}")
        
        df_combined = pd.concat(all_data, ignore_index=True)
        
        # Reorder columns
        cols = ['Athlete', 'Jornada', 'Session', 'Posicao', 'Sono', 'Stress', 
                'Fadiga', 'DOMS', 'Volume', 'RPE', 'Carga']
        df_combined = df_combined[cols]
        
        # Sort
        df_combined = df_combined.sort_values(['Jornada', 'Athlete', 'Session']).reset_index(drop=True)
        
        # Save combined file
        combined_path = input_dir / 'ALL_PSE_LONG.csv'
        df_combined.to_csv(combined_path, index=False, encoding='utf-8')
        
        print(f"\n✅ Combined file saved: {combined_path}")
        print(f"   Total records: {len(df_combined)}")
        print(f"   Jornadas: {df_combined['Jornada'].unique().tolist()}")
        print(f"   Unique athletes: {df_combined['Athlete'].nunique()}")
        
        print(f"\n📊 Sample from combined file:")
        print(df_combined.head(10).to_string(index=False))


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Transform PSE wide format CSV files to long format.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transform single file
  python transform_pse_wide_to_long.py Jogo1_pse.csv
  
  # Transform all files in directory
  python transform_pse_wide_to_long.py --dir C:\\dadosPSE
  
  # Specify output location
  python transform_pse_wide_to_long.py Jogo1_pse.csv output_long.csv
        """
    )
    
    parser.add_argument('input', nargs='?',
                       help='Input PSE CSV file or directory with --dir flag')
    parser.add_argument('output', nargs='?', default=None,
                       help='Output CSV file (optional)')
    parser.add_argument('--dir', action='store_true',
                       help='Process all PSE files in directory')
    
    args = parser.parse_args()
    
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.dir:
            # Process directory
            transform_all_pse_files(args.input, args.output)
        else:
            # Process single file
            parse_pse_wide_format(args.input, args.output)
        
        print("\n✅ Transformation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
