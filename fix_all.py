# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 경매/공매 마커 모양 다르게 - 경매는 원, 공매는 사각형, 글자 추가
old_marker_svg = '''var size=(name==='auction'||name==='public')?12:16;
var svg='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'"><circle cx="'+(size/2)+'" cy="'+(size/2)+'" r="'+(size/2-1)+'" fill="'+a._color+'" stroke="#fff" stroke-width="2"/></svg>');
var img=new kakao.maps.MarkerImage(svg,new kakao.maps.Size(size,size),{offset:new kakao.maps.Point(size/2,size/2)});'''

new_marker_svg = '''var size=20;
var svg;
if(name==='auction'){
// 경매: 파란 원 + 경 글자
svg='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'"><circle cx="'+(size/2)+'" cy="'+(size/2)+'" r="'+(size/2-1)+'" fill="#2196F3" stroke="#fff" stroke-width="2"/><text x="'+(size/2)+'" y="'+(size/2+4)+'" font-size="10" fill="#fff" text-anchor="middle" font-weight="bold">경</text></svg>');
}else if(name==='public'){
// 공매: 보라 사각형 + 공 글자
svg='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'"><rect x="1" y="1" width="'+(size-2)+'" height="'+(size-2)+'" rx="3" fill="#9C27B0" stroke="#fff" stroke-width="2"/><text x="'+(size/2)+'" y="'+(size/2+4)+'" font-size="10" fill="#fff" text-anchor="middle" font-weight="bold">공</text></svg>');
}else if(name==='inside'){
// 지구내: 녹색 원
svg='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'"><circle cx="'+(size/2)+'" cy="'+(size/2)+'" r="'+(size/2-1)+'" fill="#4CAF50" stroke="#fff" stroke-width="2"/><text x="'+(size/2)+'" y="'+(size/2+4)+'" font-size="9" fill="#fff" text-anchor="middle" font-weight="bold">내</text></svg>');
}else if(name==='nearby'){
// 근처: 주황 원
svg='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'"><circle cx="'+(size/2)+'" cy="'+(size/2)+'" r="'+(size/2-1)+'" fill="#FF9800" stroke="#fff" stroke-width="2"/><text x="'+(size/2)+'" y="'+(size/2+4)+'" font-size="9" fill="#fff" text-anchor="middle" font-weight="bold">근</text></svg>');
}else{
svg='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'"><circle cx="'+(size/2)+'" cy="'+(size/2)+'" r="'+(size/2-1)+'" fill="'+a._color+'" stroke="#fff" stroke-width="2"/></svg>');
}
var img=new kakao.maps.MarkerImage(svg,new kakao.maps.Size(size,size),{offset:new kakao.maps.Point(size/2,size/2)});'''

content = content.replace(old_marker_svg, new_marker_svg)

# 2. showParcel 함수에 더 나은 에러 핸들링 추가
old_showparcel = '''fetch(url).then(function(r){return r.json();}).then(function(d){
if(!d.features||!d.features.length){console.log('No parcel data');return;}'''

new_showparcel = '''fetch(url).then(function(r){
if(!r.ok){console.log('API 응답 오류:',r.status);return null;}
return r.json();
}).then(function(d){
if(!d){console.log('응답 없음');return;}
if(!d.features||!d.features.length){console.log('필지 데이터 없음, 좌표:',lat,lng);alert('해당 위치의 필지 정보를 찾을 수 없습니다.');return;}
console.log('필지 데이터 수신:',d.features.length,'개');'''

content = content.replace(old_showparcel, new_showparcel)

# 3. 폴리곤 생성 후 확인 로그 추가
old_poly_create = '''curPoly=new kakao.maps.Polygon({
path:path,
strokeWeight:4,
strokeColor:'#000',
strokeOpacity:0.9,
fillColor:col,
fillOpacity:0.5,
map:map'''

new_poly_create = '''console.log('폴리곤 생성, 꼭지점 수:',path.length);
curPoly=new kakao.maps.Polygon({
path:path,
strokeWeight:4,
strokeColor:'#000',
strokeOpacity:1,
fillColor:col,
fillOpacity:0.6,
map:map'''

content = content.replace(old_poly_create, new_poly_create)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("완료!")
print("- 경매: 파란 원 + '경' 글자")
print("- 공매: 보라 사각형 + '공' 글자")
print("- 지구내: 녹색 원 + '내' 글자")
print("- 근처: 주황 원 + '근' 글자")
print("- 폴리곤 디버깅 로그 추가")
