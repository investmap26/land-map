# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 중심점 계산 부분 수정 - MultiPolygon 처리
old_center_calc = '''d.features.forEach(function(f){
if(!f.geometry||!f.geometry.coordinates)return;
var cs=f.geometry.coordinates[0];
var cx=0,cy=0;
cs.forEach(function(c){cx+=c[0];cy+=c[1];});'''

new_center_calc = '''d.features.forEach(function(f){
if(!f.geometry||!f.geometry.coordinates)return;
var cs=f.geometry.type==='MultiPolygon'?f.geometry.coordinates[0][0]:f.geometry.coordinates[0];
if(!cs||!cs.length)return;
var cx=0,cy=0;
cs.forEach(function(c){cx+=c[0];cy+=c[1];});'''

content = content.replace(old_center_calc, new_center_calc)

# 2. 폴리곤 path 생성 부분 수정 - MultiPolygon 처리
old_path_create = '''if(!best)return;

var path=best.geometry.coordinates[0].map(function(c){'''

new_path_create = '''if(!best)return;

var coords=best.geometry.type==='MultiPolygon'?best.geometry.coordinates[0][0]:best.geometry.coordinates[0];
console.log('좌표 개수:',coords.length,'geometry 타입:',best.geometry.type);
var path=coords.map(function(c){'''

content = content.replace(old_path_create, new_path_create)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("완료!")
print("- MultiPolygon 타입 처리 추가")
print("- 중심점 계산 및 path 생성 모두 수정")
