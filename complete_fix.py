# -*- coding: utf-8 -*-
import re

VWORLD_API_KEY = "D0F229B6-968D-3F5F-B4EB-E509962F466C"

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ========== 1. 체크박스 기본 해제 ==========
content = content.replace('id="chkInside" checked', 'id="chkInside"')
content = content.replace('id="chkNearby" checked', 'id="chkNearby"')
content = content.replace('id="chkProj" checked', 'id="chkProj"')
content = content.replace('id="chkRail" checked', 'id="chkRail"')
content = content.replace('id="chkHighway" checked', 'id="chkHighway"')
content = content.replace('id="chkDev" checked', 'id="chkDev"')

# ========== 2. 마커 크기 키우기 ==========
content = content.replace("var size=name==='other'?4:7;", "var size=name==='other'?10:16;")
content = content.replace("var stroke=name==='other'?0.5:1;", "var stroke=name==='other'?1:2;")

# ========== 3. 변수 추가 ==========
old_vars = "var allMarkers=[];"
new_vars = """var allMarkers=[];
var auctionData={inside:[],nearby:[],other:[]};
var displayedMarkers=[];
var showAuction={inside:false,nearby:false,other:false};
var curPoly=null;
var VWORLD_KEY='""" + VWORLD_API_KEY + """';"""
content = content.replace(old_vars, new_vars)

# ========== 4. addAuctions 함수 수정 - 데이터만 저장 ==========
old_addauctions = r"function addAuctions\(arr,name,color\)\{[\s\S]*?allMarkers\.push\(\{marker:m,data:a,layer:name\}\);\s*\}\);\s*\}"

new_addauctions = """function addAuctions(arr,name,color){
arr.forEach(function(a){
a._color=color;
a._name=name;
});
auctionData[name]=arr;
}"""
content = re.sub(old_addauctions, new_addauctions, content)

# ========== 5. toggle 함수 수정 ==========
old_toggle = r"function toggle\(n\)\{[\s\S]*?layers\[n\]\.forEach\(function\(o\)\{o\.setMap\(show\?map:null\)\}\);\s*\}"

new_toggle = """function toggle(n){
var id='chk'+n.charAt(0).toUpperCase()+n.slice(1);
var chk=document.getElementById(id);
var show=chk?chk.checked:false;

// 경매 레이어
if(n==='inside'||n==='nearby'||n==='other'){
showAuction[n]=show;
refreshAuctionMarkers();
}else{
// 철도, 고속도로, 개발, 사업경계
layers[n].forEach(function(o){o.setMap(show?map:null);});
}
}"""
content = re.sub(old_toggle, new_toggle, content)

# ========== 6. init 함수 수정 ==========
old_init_end = "toggle('other');  // 기타는 기본 숨김\n}"
new_init_end = """// 모든 레이어 숨김
['inside','nearby','other','proj','rail','highway','dev'].forEach(function(n){toggle(n);});

// 지도 이벤트
kakao.maps.event.addListener(map,'idle',refreshAuctionMarkers);
kakao.maps.event.addListener(map,'click',function(){
if(curPoly){curPoly.setMap(null);curPoly=null;}
});
}"""
content = content.replace(old_init_end, new_init_end)

# ========== 7. 경매 마커 갱신 함수 추가 ==========
refresh_func = """
// 뷰포트 내 경매 마커만 표시
function refreshAuctionMarkers(){
// 기존 마커 제거
displayedMarkers.forEach(function(m){m.setMap(null);});
displayedMarkers=[];

var bounds=map.getBounds();
if(!bounds)return;
var sw=bounds.getSouthWest(),ne=bounds.getNorthEast();
var minLat=sw.getLat(),maxLat=ne.getLat(),minLng=sw.getLng(),maxLng=ne.getLng();

var total=0,maxShow=300;

['inside','nearby','other'].forEach(function(name){
if(!showAuction[name])return;
var arr=auctionData[name];
if(!arr)return;

arr.forEach(function(a){
if(total>=maxShow)return;
if(a.lat<minLat||a.lat>maxLat||a.lng<minLng||a.lng>maxLng)return;

var size=name==='other'?10:16;
var svg='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'"><circle cx="'+(size/2)+'" cy="'+(size/2)+'" r="'+(size/2-1)+'" fill="'+a._color+'" stroke="#fff" stroke-width="2"/></svg>');
var img=new kakao.maps.MarkerImage(svg,new kakao.maps.Size(size,size),{offset:new kakao.maps.Point(size/2,size/2)});
var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(a.lat,a.lng),image:img,map:map});

var info=new kakao.maps.InfoWindow({content:'<div style="padding:10px;font-size:12px;max-width:280px;line-height:1.5"><b style="font-size:14px">'+a.case_no+'</b><br>'+a.address+'<br>용도: '+a.usage+'<br>감정가: '+(a.appraisal/10000).toLocaleString()+'만원<br>최저가: '+(a.min_price/10000).toLocaleString()+'만원 ('+a.ratio+')<br>상태: '+a.status+' | '+a.date+'</div>'});

kakao.maps.event.addListener(m,'mouseover',function(){info.open(map,m);});
kakao.maps.event.addListener(m,'mouseout',function(){info.close();});
kakao.maps.event.addListener(m,'click',function(){showParcel(a.lat,a.lng,name);});

displayedMarkers.push(m);
total++;
});
});
}

// 필지 폴리곤 표시
function showParcel(lat,lng,type){
if(curPoly){curPoly.setMap(null);curPoly=null;}
map.setCenter(new kakao.maps.LatLng(lat,lng));
map.setLevel(1);

var x=lng*20037508.34/180;
var y=Math.log(Math.tan((90+lat)*Math.PI/360))/(Math.PI/180)*20037508.34/180;
var bbox=(x-50)+','+(y-50)+','+(x+50)+','+(y+50);
var url='https://api.vworld.kr/req/wfs?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=lp_pa_cbnd_bubun&BBOX='+bbox+'&SRSNAME=EPSG:900913&OUTPUT=application/json&KEY='+VWORLD_KEY+'&DOMAIN=c820131-bit.github.io';

fetch(url).then(function(r){return r.json();}).then(function(d){
if(!d.features||!d.features.length){console.log('No parcel data');return;}

var best=null,minD=Infinity;
d.features.forEach(function(f){
if(!f.geometry||!f.geometry.coordinates)return;
var cs=f.geometry.coordinates[0];
var cx=0,cy=0;
cs.forEach(function(c){cx+=c[0];cy+=c[1];});
cx/=cs.length;cy/=cs.length;
var dist=Math.sqrt((cx-x)*(cx-x)+(cy-y)*(cy-y));
if(dist<minD){minD=dist;best=f;}
});

if(!best)return;

var path=best.geometry.coordinates[0].map(function(c){
var lon=c[0]*180/20037508.34;
var la=Math.atan(Math.exp(c[1]*Math.PI/20037508.34))*360/Math.PI-90;
return new kakao.maps.LatLng(la,lon);
});

var col=type==='inside'?'#4CAF50':type==='nearby'?'#FF9800':'#9E9E9E';
curPoly=new kakao.maps.Polygon({
path:path,
strokeWeight:4,
strokeColor:'#000',
strokeOpacity:0.9,
fillColor:col,
fillOpacity:0.5,
map:map
});
}).catch(function(e){console.log('API error:',e);});
}
"""

# closeRoadview 함수 뒤에 삽입
pattern = r"function closeRoadview\(\)\{[^}]+\}"
match = re.search(pattern, content)
if match:
    content = content[:match.end()] + refresh_func + content[match.end():]

# ========== 8. 사업경계, 철도, 고속도로, 개발 - map 제거 ==========
# 처음에 숨기기 위해 map:map 제거
content = content.replace(
    ",map:map});",
    "});"
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("완료!")
print("- 처음에 빈 지도")
print("- 체크박스로 레이어 선택")
print("- 뷰포트 내 최대 300개 마커")
print("- 마커 클릭 시 필지 폴리곤")
print("- 철도/고속도로/개발/사업경계 정상 작동")
