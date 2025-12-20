# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 기존 showParcel 함수를 카카오맵 지적도 레이어 방식으로 완전히 교체
old_showParcel_start = "function showParcel(lat,lng,type){"
old_showParcel_end = "}).catch(function(e){alert('에러: '+e);});\n}"

# 함수 전체 찾기
import re
pattern = r"function showParcel\(lat,lng,type\)\{[\s\S]*?\}\)\.catch\(function\(e\)\{alert\('에러: '\+e\);\}\);\n\}"
match = re.search(pattern, content)

if match:
    old_func = match.group(0)

    # 새로운 간단한 함수 - 카카오맵 지적도 레이어 사용
    new_func = '''function showParcel(lat,lng,type){
// 기존 폴리곤 제거
if(curPoly){curPoly.setMap(null);curPoly=null;}

// 해당 위치로 이동 및 확대
map.setCenter(new kakao.maps.LatLng(lat,lng));
map.setLevel(1);

// 지적도 레이어 표시 (USE_DISTRICT)
if(!map.getOverlayMapTypeId || map.getOverlayMapTypeId() !== kakao.maps.MapTypeId.USE_DISTRICT){
map.addOverlayMapTypeId(kakao.maps.MapTypeId.USE_DISTRICT);
}

// 클릭 위치에 원 표시
var col=type==='inside'?'#4CAF50':type==='nearby'?'#FF9800':type==='auction'?'#2196F3':type==='public'?'#9C27B0':'#9E9E9E';
curPoly=new kakao.maps.Circle({
center:new kakao.maps.LatLng(lat,lng),
radius:15,
strokeWeight:3,
strokeColor:col,
strokeOpacity:1,
fillColor:col,
fillOpacity:0.3,
map:map
});
}'''

    content = content.replace(old_func, new_func)
    print("showParcel 함수 교체 완료")
else:
    print("함수를 찾지 못함, 수동으로 교체 시도")
    # 수동 교체
    content = re.sub(
        r"function showParcel\(lat,lng,type\)\{[\s\S]*?catch\(function\(e\)\{[^}]*\}\);[\s\S]*?\}",
        '''function showParcel(lat,lng,type){
if(curPoly){curPoly.setMap(null);curPoly=null;}
map.setCenter(new kakao.maps.LatLng(lat,lng));
map.setLevel(1);
if(!map.getOverlayMapTypeId || map.getOverlayMapTypeId() !== kakao.maps.MapTypeId.USE_DISTRICT){
map.addOverlayMapTypeId(kakao.maps.MapTypeId.USE_DISTRICT);
}
var col=type==='inside'?'#4CAF50':type==='nearby'?'#FF9800':type==='auction'?'#2196F3':type==='public'?'#9C27B0':'#9E9E9E';
curPoly=new kakao.maps.Circle({
center:new kakao.maps.LatLng(lat,lng),
radius:15,
strokeWeight:3,
strokeColor:col,
strokeOpacity:1,
fillColor:col,
fillOpacity:0.3,
map:map
});
}''',
        content,
        count=1
    )

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("완료! 카카오맵 지적도 레이어 방식으로 변경")
