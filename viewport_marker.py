# -*- coding: utf-8 -*-
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 변수 추가 (allMarkers 다음에)
old_vars = "var allMarkers=[];"
new_vars = """var allMarkers=[];
var visibleMarkers={inside:[],nearby:[],other:[]};
var showLayer={inside:false,nearby:false,other:false};"""
content = content.replace(old_vars, new_vars)

# 2. addAuctions 함수 완전 교체 - 마커 생성만 하고 표시는 안함
old_add_auctions_start = "function addAuctions(arr,name,color){"
old_add_auctions_pattern = r"function addAuctions\(arr,name,color\)\{[\s\S]*?layers\[name\]\.push\(m\);\s*allMarkers\.push\(\{marker:m,data:a,layer:name\}\);\s*\}\);\s*\}"

new_add_auctions = """function addAuctions(arr,name,color){
var size=name==='other'?8:14;
var stroke=name==='other'?1:2;
arr.forEach(function(a){
a._color=color;
a._size=size;
a._stroke=stroke;
a._layer=name;
});
}"""

content = re.sub(old_add_auctions_pattern, new_add_auctions, content)

# 3. toggle 함수 교체 - 뷰포트 기반으로
old_toggle = r"function toggle\(n\)\{[\s\S]*?layers\[n\]\.forEach\(function\(o\)\{o\.setMap\(show\?map:null\)\}\);\s*\}"

new_toggle = """function toggle(n){
var id='chk'+n.charAt(0).toUpperCase()+n.slice(1);
var chk=document.getElementById(id);
showLayer[n]=chk?chk.checked:false;
updateVisibleMarkers();
}"""

content = re.sub(old_toggle, new_toggle, content)

# 4. init 함수 끝에 뷰포트 이벤트 추가
old_init_end = """addDev();
kakao.maps.event.addListener(map,'click',function(){if(curPoly){curPoly.setMap(null);curPoly=null;}});
}"""

new_init_end = """addDev();
kakao.maps.event.addListener(map,'click',function(){if(curPoly){curPoly.setMap(null);curPoly=null;}});
kakao.maps.event.addListener(map,'idle',updateVisibleMarkers);
kakao.maps.event.addListener(map,'zoom_changed',updateVisibleMarkers);
}"""

content = content.replace(old_init_end, new_init_end)

# 5. updateVisibleMarkers 함수 추가 (showParcel 함수 앞에)
update_func = """
// 뷰포트 내 마커만 표시
function updateVisibleMarkers(){
var bounds=map.getBounds();
var sw=bounds.getSouthWest();
var ne=bounds.getNorthEast();
var minLat=sw.getLat(),maxLat=ne.getLat();
var minLng=sw.getLng(),maxLng=ne.getLng();

['inside','nearby','other'].forEach(function(name){
// 기존 마커 제거
visibleMarkers[name].forEach(function(m){m.setMap(null);});
visibleMarkers[name]=[];

if(!showLayer[name])return;

var arr=name==='inside'?inside:name==='nearby'?nearby:other;
var count=0;
var maxMarkers=500; // 최대 표시 개수

arr.forEach(function(a){
if(count>=maxMarkers)return;
if(a.lat>=minLat&&a.lat<=maxLat&&a.lng>=minLng&&a.lng<=maxLng){
var svg='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="'+a._size+'" height="'+a._size+'"><circle cx="'+(a._size/2)+'" cy="'+(a._size/2)+'" r="'+(a._size/2-1)+'" fill="'+a._color+'" stroke="#fff" stroke-width="'+a._stroke+'"/></svg>');
var img=new kakao.maps.MarkerImage(svg,new kakao.maps.Size(a._size,a._size),{offset:new kakao.maps.Point(a._size/2,a._size/2)});
var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(a.lat,a.lng),image:img,map:map});
var info=new kakao.maps.InfoWindow({content:'<div style="padding:8px;font-size:12px;min-width:200px"><b>'+a.case_no+'</b><br>'+a.address+'<br>용도:'+a.usage+'<br>감정가:'+(a.appraisal/10000).toLocaleString()+'만<br>최저가:'+(a.min_price/10000).toLocaleString()+'만('+a.ratio+')<br>'+a.status+' '+a.date+'</div>'});
kakao.maps.event.addListener(m,'mouseover',function(){info.open(map,m);});
kakao.maps.event.addListener(m,'mouseout',function(){info.close();});
kakao.maps.event.addListener(m,'click',function(){showParcel(a.lat,a.lng,name);});
visibleMarkers[name].push(m);
count++;
}
});
});
}

"""

# showParcel 함수 앞에 삽입
if 'var VWORLD_KEY=' in content:
    vworld_pos = content.find('var VWORLD_KEY=')
    content = content[:vworld_pos] + update_func + content[vworld_pos:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("완료!")
print("- 현재 화면 영역 내 마커만 표시")
print("- 화면당 최대 500개 마커")
print("- 지도 이동/확대 시 자동 갱신")
