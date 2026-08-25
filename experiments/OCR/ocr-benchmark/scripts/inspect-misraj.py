from pathlib import Path
import pyarrow.parquet as pq


DATA_DIR = Path("data/raw/misraj/data")


for parquet_file in sorted(DATA_DIR.glob("*.parquet")):
    print("=" * 80)
    print(f"FILE: {parquet_file.name}")

    parquet = pq.ParquetFile(parquet_file)

    print(f"Rows: {parquet.metadata.num_rows}")
    print(f"Row groups: {parquet.num_row_groups}")

    print("\nSchema:")
    print(parquet.schema_arrow)


# Inspect 3 Misraj samples

parquet_file = sorted(DATA_DIR.glob("*.parquet"))[0]

table = pq.read_table(parquet_file)

print(f"Columns: {table.column_names}")
print(f"Total rows: {table.num_rows}")

rows = table.slice(0, 3).to_pylist()

for i, row in enumerate(rows, start=1):
    print("\n" + "=" * 80)
    print(f"SAMPLE {i}")
    print("=" * 80)

    print(f"\nUUID:\n{row['uuid']}")

    print("\nIMAGE:")
    print(f"Path: {row['image']['path']}")

    image_bytes = row["image"]["bytes"]
    print(f"Bytes: {len(image_bytes):,}")

    print("\nMARKDOWN:")
    print(row["markdown"][:3000])