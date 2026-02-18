"""
Transform Wide Format Performance Data to Long Format
====================================================

Converts Excel data from wide format (one column per session) to long format
(one row per athlete-session combination) for database ingestion.

Example Input (Wide Format):
----------------------------
Athlete | RPE_T1 | RPE_T2 | DOMS_T1 | DOMS_T2 | Distance_T1 | Distance_T2
ANDRADE |   8    |   7    |    3    |    4    |   5000      |   4800
CARDOSO |   7    |   8    |    2    |    3    |   4900      |   5100

Example Output (Long Format):
-----------------------------
Athlete | Session | RPE | DOMS | Distance
ANDRADE |   T1    |  8  |  3   |  5000
ANDRADE |   T2    |  7  |  4   |  4800
CARDOSO |   T1    |  7  |  2   |  4900
CARDOSO |   T2    |  8  |  3   |  5100

Usage:
------
python scripts/transform_wide_to_long.py input.xlsx output.csv
"""

import pandas as pd
import sys
from pathlib import Path
import re
from typing import List, Dict


def extract_session_from_column(col_name: str) -> str:
    """
    Extract session identifier from column name.
    
    Examples:
        'RPE_T1' -> 'T1'
        'DOMS_Jogo2' -> 'Jogo2'
        'Distance_Session_3' -> 'Session_3'
    """
    parts = col_name.split('_')
    if len(parts) > 1:
        return '_'.join(parts[1:])  # Everything after first underscore
    return col_name


def extract_metric_from_column(col_name: str) -> str:
    """
    Extract metric name from column name.
    
    Examples:
        'RPE_T1' -> 'RPE'
        'DOMS_Jogo2' -> 'DOMS'
        'Distance_Session_3' -> 'Distance'
    """
    return col_name.split('_')[0]


def identify_column_pattern(df: pd.DataFrame, athlete_col: str = None) -> Dict[str, List[str]]:
    """
    Identify which columns belong to which sessions based on naming patterns.
    
    Returns:
        Dict mapping session identifiers to their metric columns
        Example: {'T1': ['RPE_T1', 'DOMS_T1', 'Distance_T1'],
                  'T2': ['RPE_T2', 'DOMS_T2', 'Distance_T2']}
    """
    # Find athlete column if not specified
    if athlete_col is None:
        # Common athlete column names
        for col in df.columns:
            if col.lower() in ['athlete', 'atleta', 'nome', 'player', 'jogador']:
                athlete_col = col
                break
    
    if athlete_col is None:
        raise ValueError("Could not identify athlete column. Please specify with --athlete-col parameter")
    
    # Group columns by session identifier
    session_columns = {}
    
    for col in df.columns:
        if col == athlete_col:
            continue
        
        # Check if column has session identifier (contains underscore)
        if '_' in col:
            session = extract_session_from_column(col)
            if session not in session_columns:
                session_columns[session] = []
            session_columns[session].append(col)
    
    return session_columns


def wide_to_long(df: pd.DataFrame, 
                 athlete_col: str = None,
                 session_pattern: str = None) -> pd.DataFrame:
    """
    Transform wide format DataFrame to long format.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame in wide format
    athlete_col : str, optional
        Name of the athlete column. Auto-detected if not provided.
    session_pattern : str, optional
        Regex pattern to extract session identifier. Auto-detected if not provided.
    
    Returns:
    --------
    pd.DataFrame
        Long format DataFrame with columns: Athlete, Session, [Metrics...]
    """
    # Auto-detect athlete column
    if athlete_col is None:
        for col in df.columns:
            if col.lower() in ['athlete', 'atleta', 'nome', 'player', 'jogador', 'name']:
                athlete_col = col
                break
    
    if athlete_col is None:
        raise ValueError("Could not identify athlete column. Specify with athlete_col parameter.")
    
    print(f"✓ Using athlete column: {athlete_col}")
    
    # Identify session columns
    session_columns = identify_column_pattern(df, athlete_col)
    
    if not session_columns:
        raise ValueError("No session columns found. Expected format: METRIC_SESSION (e.g., RPE_T1, DOMS_T2)")
    
    print(f"✓ Found {len(session_columns)} sessions: {', '.join(session_columns.keys())}")
    
    # Collect all long format data
    long_data = []
    
    for _, row in df.iterrows():
        athlete_name = row[athlete_col]
        
        # Skip empty rows
        if pd.isna(athlete_name) or str(athlete_name).strip() == '':
            continue
        
        # Create one row per session
        for session_id, columns in session_columns.items():
            session_row = {
                'Athlete': athlete_name,
                'Session': session_id
            }
            
            # Extract metrics for this session
            for col in columns:
                metric_name = extract_metric_from_column(col)
                value = row[col]
                
                # Keep original value (NaN, numeric, or string)
                session_row[metric_name] = value
            
            long_data.append(session_row)
    
    # Create long format DataFrame
    df_long = pd.DataFrame(long_data)
    
    # Reorder columns: Athlete, Session, then alphabetically sorted metrics
    metric_cols = sorted([col for col in df_long.columns if col not in ['Athlete', 'Session']])
    df_long = df_long[['Athlete', 'Session'] + metric_cols]
    
    print(f"✓ Transformed {len(df)} athletes × {len(session_columns)} sessions = {len(df_long)} rows")
    
    return df_long


def transform_file(input_path: str, 
                   output_path: str = None,
                   athlete_col: str = None,
                   sheet_name: int = 0,
                   csv_separator: str = ',') -> pd.DataFrame:
    """
    Transform a wide format file to long format.
    
    Parameters:
    -----------
    input_path : str
        Path to input file (.xlsx, .xls, or .csv)
    output_path : str, optional
        Path to output CSV file. If None, uses input_name_long.csv
    athlete_col : str, optional
        Name of athlete column. Auto-detected if not provided.
    sheet_name : int or str, optional
        Excel sheet to read (default: 0 = first sheet)
    csv_separator : str, optional
        CSV separator for input files (default: ',')
    
    Returns:
    --------
    pd.DataFrame
        Transformed long format DataFrame
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    print(f"\n📂 Reading: {input_path.name}")
    
    # Read input file
    if input_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(input_path, sheet_name=sheet_name)
        print(f"   Excel sheet: {sheet_name}")
    elif input_path.suffix.lower() == '.csv':
        df = pd.read_csv(input_path, sep=csv_separator)
        print(f"   CSV separator: '{csv_separator}'")
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")
    
    print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Transform to long format
    df_long = wide_to_long(df, athlete_col=athlete_col)
    
    # Determine output path
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_long.csv"
    else:
        output_path = Path(output_path)
    
    # Save output
    df_long.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\n✅ Saved: {output_path}")
    print(f"   Shape: {df_long.shape[0]} rows × {df_long.shape[1]} columns")
    
    # Show preview
    print("\n📊 Preview (first 10 rows):")
    print(df_long.head(10).to_string(index=False))
    
    # Show statistics
    print(f"\n📈 Statistics:")
    print(f"   Unique athletes: {df_long['Athlete'].nunique()}")
    print(f"   Unique sessions: {df_long['Session'].nunique()}")
    print(f"   Total records: {len(df_long)}")
    
    # Show metrics
    metrics = [col for col in df_long.columns if col not in ['Athlete', 'Session']]
    print(f"   Metrics: {', '.join(metrics)}")
    
    # Check for missing values
    missing_summary = df_long[metrics].isna().sum()
    if missing_summary.any():
        print(f"\n⚠️ Missing values detected:")
        for metric, count in missing_summary[missing_summary > 0].items():
            pct = (count / len(df_long)) * 100
            print(f"   {metric}: {count} ({pct:.1f}%)")
    else:
        print(f"\n✓ No missing values in metrics")
    
    return df_long


def main():
    """Command-line interface for the transformation script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Transform wide format performance data to long format for database ingestion.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (auto-detect athlete column)
  python transform_wide_to_long.py data.xlsx
  
  # Specify output file
  python transform_wide_to_long.py data.xlsx output.csv
  
  # Specify athlete column name
  python transform_wide_to_long.py data.xlsx --athlete-col "Nome"
  
  # Read specific Excel sheet
  python transform_wide_to_long.py data.xlsx --sheet 1
  
  # CSV input with semicolon separator
  python transform_wide_to_long.py data.csv --csv-sep ";"
        """
    )
    
    parser.add_argument('input_file', 
                       help='Input file (.xlsx, .xls, or .csv)')
    parser.add_argument('output_file', nargs='?', default=None,
                       help='Output CSV file (optional, default: INPUT_long.csv)')
    parser.add_argument('--athlete-col', '-a', 
                       help='Name of athlete column (auto-detected if not specified)')
    parser.add_argument('--sheet', '-s', default=0,
                       help='Excel sheet name or index (default: 0)')
    parser.add_argument('--csv-sep', default=',',
                       help='CSV separator (default: ,)')
    
    args = parser.parse_args()
    
    try:
        df_long = transform_file(
            input_path=args.input_file,
            output_path=args.output_file,
            athlete_col=args.athlete_col,
            sheet_name=args.sheet,
            csv_separator=args.csv_sep
        )
        
        print("\n✅ Transformation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
