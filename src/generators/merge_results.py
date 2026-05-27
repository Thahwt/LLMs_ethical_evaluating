from pathlib import Path

# Khởi tạo đường dẫn bằng Object của Pathlib
results_dir = Path("data/results/")
output_file = results_dir / "merged_responses.jsonl"

# Quét file .jsonl và loại trừ file output
jsonl_files = [
    f for f in results_dir.glob("*.jsonl")
    if f.resolve() != output_file.resolve()
]

print(f"Tìm thấy {len(jsonl_files)} file cần gộp...")

# Ghi file với pathlib
with output_file.open("w", encoding="utf-8") as outfile:
    for file_path in jsonl_files:
        print(f"  + Đang gộp: {file_path.name}")
        with file_path.open("r", encoding="utf-8") as infile:
            for line in infile:
                if line.strip():
                    outfile.write(line.strip() + "\n")

print(f"Đã gộp thành công tất cả dữ liệu vào file: {output_file}")