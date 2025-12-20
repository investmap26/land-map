# -*- coding: utf-8 -*-
import re
import json
from collections import Counter

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# other 배열에서 case_no 추출
match = re.search(r'var other=(\[[\s\S]*?\]);', content)
if match:
    try:
        # JSON 파싱 시도
        data = json.loads(match.group(1))

        # case_no 앞자리 패턴 분석
        prefixes = Counter()
        for item in data[:100]:  # 처음 100개만 확인
            case_no = item.get('case_no', '')
            # 앞 몇 글자 추출
            prefix = case_no[:4] if len(case_no) >= 4 else case_no
            prefixes[prefix] += 1

        print("case_no 앞자리 패턴 (처음 100개):")
        for prefix, count in prefixes.most_common(20):
            print(f"  {prefix}: {count}개")

        # 전체 데이터에서 패턴 확인
        print(f"\n전체 기타 데이터 수: {len(data)}개")

        # 숫자로 시작하는 것과 아닌 것 구분
        numeric_start = 0
        alpha_start = 0
        patterns = Counter()

        for item in data:
            case_no = item.get('case_no', '')
            if case_no:
                first_char = case_no[0]
                if first_char.isdigit():
                    numeric_start += 1
                else:
                    alpha_start += 1
                    patterns[case_no[:10]] += 1

        print(f"\n숫자로 시작: {numeric_start}개")
        print(f"문자로 시작: {alpha_start}개")

        if alpha_start > 0:
            print("\n문자로 시작하는 case_no 예시:")
            for p, c in patterns.most_common(10):
                print(f"  {p}...: {c}개")

    except Exception as e:
        print(f"파싱 오류: {e}")
