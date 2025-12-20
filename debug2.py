# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# showParcel 함수 시작 부분에 alert 추가
old_start = '''function showParcel(lat,lng,type){
console.log('showParcel 호출:', lat, lng, type);'''

new_start = '''function showParcel(lat,lng,type){
alert('1. 클릭됨: '+lat+', '+lng);'''

content = content.replace(old_start, new_start)

# API 호출 전 alert
old_fetch = '''console.log('API 호출 시작');
fetch(url)'''

new_fetch = '''alert('2. API URL: '+url.substring(0,80)+'...');
fetch(url)'''

content = content.replace(old_fetch, new_fetch)

# API 응답 후 alert
old_response = '''console.log('API 응답:', r.status);'''
new_response = '''alert('3. 응답 status: '+r.status);'''
content = content.replace(old_response, new_response)

# 데이터 수신 후 alert
old_data = '''console.log('필지 데이터:', d.features?d.features.length:0);'''
new_data = '''alert('4. 필지 수: '+(d.features?d.features.length:0));'''
content = content.replace(old_data, new_data)

# 폴리곤 생성 alert
old_poly = '''console.log('폴리곤 생성:', coords.length);'''
new_poly = '''alert('5. 폴리곤 꼭지점: '+coords.length);'''
content = content.replace(old_poly, new_poly)

# 완료 alert
old_done = '''console.log('폴리곤 완료');'''
new_done = '''alert('6. 완료!');'''
content = content.replace(old_done, new_done)

# 에러 alert
old_err = '''console.log('API 에러:', e);'''
new_err = '''alert('에러: '+e);'''
content = content.replace(old_err, new_err)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("디버깅 alert 추가 완료")
