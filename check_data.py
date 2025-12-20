# -*- coding: utf-8 -*-
import re
import json

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# other 배열의 첫 번째 항목 추출
match = re.search(r'var other=\[(\{[^}]+\})', content)
if match:
    try:
        item = json.loads(match.group(1))
        print("첫 번째 기타 항목의 필드:")
        for key, value in item.items():
            print(f"  {key}: {value}")
    except:
        print(match.group(1)[:500])
