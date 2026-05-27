import os
import sys
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Thêm thư mục gốc vào đường dẫn hệ thống để import thư viện từ thư mục src
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import trực tiếp class ModelClient mà bạn đã hoàn thiện
from src.evaluators.model_runner import ModelClient

# Load các API keys từ file .env
load_dotenv()


def run_test(config_path="configs/models.yaml"):
    print(f"Đang tải cấu hình từ: {config_path}")

    if not os.path.exists(config_path):
        print("Lỗi: Không tìm thấy file models.yaml. Hãy chắc chắn bạn đang chạy ở thư mục gốc!")
        return

    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    models = cfg.get("llms", []) + cfg.get("slms", [])
    print(f"Bắt đầu kiểm tra {len(models)} models...\n" + "=" * 50)

    # Một prompt rất ngắn để tiết kiệm token và test tốc độ phản hồi
    test_prompt = "Xin chào, hãy trả lời đúng 1 câu ngắn gọn bằng tiếng Việt: 'Kết nối thành công!'"

    for model_cfg in models:
        print(f"Đang gọi model : {model_cfg['name']}")
        print(f"Provider     : {model_cfg['provider']}")
        print(f"Model ID     : {model_cfg['model_id']}")

        try:
            # Khởi tạo client
            client = ModelClient(model_cfg)

            # Yêu cầu sinh text với giới hạn token siêu nhỏ để test
            response = client.generate(test_prompt, max_tokens=20)

            print(f"Phản hồi     : {response.strip()}")
            print("-" * 50)

        except Exception as e:
            print(f"Lỗi kết nối  : {str(e)}")
            print("-" * 50)


if __name__ == "__main__":
    run_test()