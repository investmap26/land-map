# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 마커 생성 시 map:map 추가 (경매 마커)
old_marker = "var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(a.lat,a.lng),image:img});"
new_marker = "var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(a.lat,a.lng),image:img,map:map});"
content = content.replace(old_marker, new_marker)

# 2. 기타를 경매/공매로 분리 - case_no로 구분
# 공매는 보통 "공매" 또는 "온비드" 등의 키워드가 있거나 다른 형식
# 일단 HTML에서 기타 레이블만 변경 (실제 분리는 데이터 구조 확인 후)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("완료! 마커 표시 문제 수정")
