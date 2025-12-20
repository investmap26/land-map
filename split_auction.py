# -*- coding: utf-8 -*-
import re
import json

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# other 배열에서 경매/공매 분류 확인
match = re.search(r'var other=(\[[\s\S]*?\]);', content)
if match:
    data = json.loads(match.group(1))

    auction_count = 0  # 타경 (경매)
    public_count = 0   # 온비드 (공매)
    unknown_count = 0  # 기타

    for item in data:
        case_no = item.get('case_no', '')
        if '타경' in case_no:
            auction_count += 1
        elif '온비드' in case_no.lower() or 'onbid' in case_no.lower():
            public_count += 1
        else:
            unknown_count += 1

    print(f"타경(경매): {auction_count}개")
    print(f"온비드(공매): {public_count}개")
    print(f"기타: {unknown_count}개")

    # 기타 case_no 샘플 확인
    if unknown_count > 0:
        print("\n기타 case_no 샘플:")
        samples = []
        for item in data:
            case_no = item.get('case_no', '')
            if '타경' not in case_no and '온비드' not in case_no.lower():
                samples.append(case_no)
                if len(samples) >= 10:
                    break
        for s in samples:
            print(f"  {s}")
