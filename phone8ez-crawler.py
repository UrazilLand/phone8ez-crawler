import json
from datetime import datetime

data = {
    "message": "크롤러 테스트 성공!",
    "timestamp": datetime.now().isoformat()
}

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ output.json 생성 완료")
