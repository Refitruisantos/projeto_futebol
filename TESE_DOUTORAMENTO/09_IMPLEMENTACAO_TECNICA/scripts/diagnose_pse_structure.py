import pandas as pd

csv_path = r'C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\dadosPSE\Jogo1_pse.csv'
df = pd.read_csv(csv_path, sep=';', header=None, encoding='utf-8')

print(f"Total columns: {df.shape[1]}\n")

# Analyze ANDRADE row (row 6, index 5)
row = df.iloc[5]

print("=" * 80)
print("ANDRADE ROW ANALYSIS")
print("=" * 80)

print("\nSession 1 (Columns 0-12):")
for i in range(13):
    print(f"  Col {i:2d}: [{row.iloc[i]}]")

print("\nSession 2 (Columns 13-25):")
for i in range(13, 26):
    print(f"  Col {i:2d}: [{row.iloc[i]}]")

print("\nSession 3 (Columns 26-38):")
for i in range(26, 39):
    print(f"  Col {i:2d}: [{row.iloc[i]}]")

print("\n" + "=" * 80)
print("HEADER ROW 2 (column names)")
print("=" * 80)
header_row = df.iloc[1]
print("\nColumns 0-12:")
for i in range(13):
    print(f"  Col {i:2d}: [{header_row.iloc[i]}]")
