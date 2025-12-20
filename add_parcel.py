# -*- coding: utf-8 -*-
import re

VWORLD_API_KEY = "D0F229B6-968D-3F5F-B4EB-E509962F466C"

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 마커 크기 키우기
content = content.replace("var size=name==='other'?4:7;", "var size=name==='other'?8:14;")
content = content.replace("var stroke=name==='other'?0.5:1;", "var stroke=name==='other'?1:2;")

# 2. 마커 클릭 이벤트 추가
old_line = "kakao.maps.event.addListener(m,'mouseout',function(){info.close()});\nm.data=a;"
new_line = """kakao.maps.event.addListener(m,'mouseout',function(){info.close()});
kakao.maps.event.addListener(m,'click',function(){showParcel(a.lat,a.lng,name);});
m.data=a;"""
content = content.replace(old_line, new_line)

# 3. init 함수에 지도 클릭 이벤트 추가
old_init = "toggle('other');  // 기타는 기본 숨김\n}"
new_init = """toggle('other');  // 기타는 기본 숨김
kakao.maps.event.addListener(map,'click',function(){if(curPoly){curPoly.setMap(null);curPoly=null;}});
}"""
content = content.replace(old_init, new_init)

# 4. 필지 표시 코드 추가 (첫번째 </script> 바로 전에)
parcel_code = '''
var VWORLD_KEY="''' + VWORLD_API_KEY + '''";
var curPoly=null;
function showParcel(lat,lng,type){
map.setCenter(new kakao.maps.LatLng(lat,lng));
map.setLevel(1);
var x=lng*20037508.34/180,y=Math.log(Math.tan((90+lat)*Math.PI/360))/(Math.PI/180)*20037508.34/180;
var url='https://api.vworld.kr/req/wfs?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=lp_pa_cbnd_bubun&BBOX='+(x-50)+','+(y-50)+','+(x+50)+','+(y+50)+'&SRSNAME=EPSG:900913&OUTPUT=application/json&KEY='+VWORLD_KEY+'&DOMAIN=c820131-bit.github.io';
fetch(url).then(r=>r.json()).then(d=>{
if(!d.features||!d.features.length)return;
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
}).catch(e=>console.log(e));
}
'''

# 첫번째 </script> 찾아서 그 앞에 삽입
first_script_end = content.find('</script>')
if first_script_end > 0:
    content = content[:first_script_end] + parcel_code + '\n' + content[first_script_end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("완료!")
