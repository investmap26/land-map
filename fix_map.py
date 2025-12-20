# -*- coding: utf-8 -*-
import re

VWORLD_API_KEY = "D0F229B6-968D-3F5F-B4EB-E509962F466C"

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 모든 체크박스 기본값을 체크 해제로 변경
content = content.replace('id="chkInside" checked', 'id="chkInside"')
content = content.replace('id="chkNearby" checked', 'id="chkNearby"')
content = content.replace('id="chkProj" checked', 'id="chkProj"')
content = content.replace('id="chkRail" checked', 'id="chkRail"')
content = content.replace('id="chkHighway" checked', 'id="chkHighway"')
content = content.replace('id="chkDev" checked', 'id="chkDev"')

# 2. addAuctions에서 map:map 제거 (처음에 표시 안함)
content = content.replace(
    "var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(a.lat,a.lng),image:img,map:map});",
    "var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(a.lat,a.lng),image:img});"
)

# 3. addRail에서도 map:map 제거
content = content.replace(
    "var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(r.lat,r.lng),image:new kakao.maps.MarkerImage(svg,new kakao.maps.Size(20,20)),map:map});",
    "var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(r.lat,r.lng),image:new kakao.maps.MarkerImage(svg,new kakao.maps.Size(20,20))});"
)

# 4. addHighway에서도 제거
content = content.replace(
    "var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(h.lat,h.lng),image:new kakao.maps.MarkerImage(svg,new kakao.maps.Size(16,10)),map:map});",
    "var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(h.lat,h.lng),image:new kakao.maps.MarkerImage(svg,new kakao.maps.Size(16,10))});"
)

# 5. addDev에서도 제거
content = content.replace(
    "var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(d.lat,d.lng),image:new kakao.maps.MarkerImage(svg,new kakao.maps.Size(12,12)),map:map});",
    "var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(d.lat,d.lng),image:new kakao.maps.MarkerImage(svg,new kakao.maps.Size(12,12))});"
)

# 6. addProjects (폴리곤)도 처음에 숨기기
content = content.replace(
    "var poly=new kakao.maps.Polygon({path:path,strokeWeight:2,strokeColor:'#1976D2',strokeOpacity:0.8,fillColor:'#1976D2',fillOpacity:0.1,map:map});",
    "var poly=new kakao.maps.Polygon({path:path,strokeWeight:2,strokeColor:'#1976D2',strokeOpacity:0.8,fillColor:'#1976D2',fillOpacity:0.1});"
)

# 7. init에서 toggle('other') 제거 (이미 다 숨겨져 있으므로)
content = content.replace("toggle('other');  // 기타는 기본 숨김\n", "")

# 8. showParcel 함수가 제대로 작동하도록 확인
# 기존 showParcel 코드가 있으면 유지, 없으면 추가
if 'function showParcel' not in content:
    parcel_code = '''
var VWORLD_KEY="''' + VWORLD_API_KEY + '''";
var curPoly=null;
function showParcel(lat,lng,type){
map.setCenter(new kakao.maps.LatLng(lat,lng));
map.setLevel(1);
var x=lng*20037508.34/180,y=Math.log(Math.tan((90+lat)*Math.PI/360))/(Math.PI/180)*20037508.34/180;
var url='https://api.vworld.kr/req/wfs?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=lp_pa_cbnd_bubun&BBOX='+(x-50)+','+(y-50)+','+(x+50)+','+(y+50)+'&SRSNAME=EPSG:900913&OUTPUT=application/json&KEY='+VWORLD_KEY+'&DOMAIN=c820131-bit.github.io';
fetch(url).then(r=>r.json()).then(d=>{
if(!d.features||!d.features.length){console.log('No features');return;}
var best=null,md=Infinity;
d.features.forEach(f=>{
if(!f.geometry)return;
var cs=f.geometry.coordinates[0],cx=0,cy=0;
cs.forEach(c=>{cx+=c[0];cy+=c[1];});
cx/=cs.length;cy/=cs.length;
var dist=Math.sqrt((cx-x)*(cx-x)+(cy-y)*(cy-y));
if(dist<md){md=dist;best=f;}
});
if(!best)return;
if(curPoly)curPoly.setMap(null);
var path=best.geometry.coordinates[0].map(c=>{
var lon=c[0]*180/20037508.34;
var la=Math.atan(Math.exp(c[1]*Math.PI/20037508.34))*360/Math.PI-90;
return new kakao.maps.LatLng(la,lon);
});
var col=type==='inside'?'#4CAF50':type==='nearby'?'#FF9800':'#9E9E9E';
curPoly=new kakao.maps.Polygon({path:path,strokeWeight:3,strokeColor:'#000',fillColor:col,fillOpacity:0.5,map:map});
}).catch(e=>console.log('API error:',e));
}
'''
    first_script_end = content.find('</script>')
    if first_script_end > 0:
        content = content[:first_script_end] + parcel_code + '\n' + content[first_script_end:]

# 9. 마커 클릭 이벤트가 없으면 추가
if "showParcel(a.lat,a.lng,name)" not in content:
    content = content.replace(
        "kakao.maps.event.addListener(m,'mouseout',function(){info.close()});\nm.data=a;",
        "kakao.maps.event.addListener(m,'mouseout',function(){info.close()});\nkakao.maps.event.addListener(m,'click',function(){showParcel(a.lat,a.lng,name);});\nm.data=a;"
    )

# 10. 지도 클릭 시 폴리곤 숨기기
if "curPoly.setMap(null)" not in content or "kakao.maps.event.addListener(map,'click'" not in content:
    # init 함수 끝에 추가
    old_init_end = "addDev();\n}"
    new_init_end = """addDev();
kakao.maps.event.addListener(map,'click',function(){if(curPoly){curPoly.setMap(null);curPoly=null;}});
}"""
    content = content.replace(old_init_end, new_init_end)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("완료!")
print("- 처음에 지도만 표시 (마커 없음)")
print("- 체크박스 클릭하면 해당 항목 표시")
print("- 마커 클릭하면 필지 폴리곤 표시")
