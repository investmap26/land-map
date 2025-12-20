# -*- coding: utf-8 -*-
import re

VWORLD_API_KEY = "D0F229B6-968D-3F5F-B4EB-E509962F466C"

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 마커 크기 키우기 (4,7 -> 10,14)
content = content.replace(
    "var size=name==='other'?4:7;",
    "var size=name==='other'?8:14;"
)
content = content.replace(
    "var stroke=name==='other'?0.5:1;",
    "var stroke=name==='other'?1:2;"
)

# 2. 마커 클릭 이벤트 추가 (mouseover/mouseout 다음에)
old_events = "kakao.maps.event.addListener(m,'mouseout',function(){info.close()});\nm.data=a;"
new_events = """kakao.maps.event.addListener(m,'mouseout',function(){info.close()});
kakao.maps.event.addListener(m,'click',function(){
    showParcel(a.lat, a.lng, name);
});
m.data=a;"""
content = content.replace(old_events, new_events)

# 3. 지도 클릭 시 폴리곤 숨기기 추가
old_init = "toggle('other');  // 기타는 기본 숨김\n}"
new_init = """toggle('other');  // 기타는 기본 숨김
kakao.maps.event.addListener(map,'click',function(e){
    if(currentPolygon){currentPolygon.setMap(null);currentPolygon=null;}
});
}"""
content = content.replace(old_init, new_init)

# 4. 필지 폴리곤 코드 추가 (closeRoadview 함수 다음에)
parcel_code = '''
// 브이월드 필지 폴리곤
var VWORLD_KEY="''' + VWORLD_API_KEY + '''";
var currentPolygon=null;

function showParcel(lat,lng,type){
    map.setCenter(new kakao.maps.LatLng(lat,lng));
    map.setLevel(1);

    var x=lng*20037508.34/180;
    var y=Math.log(Math.tan((90+lat)*Math.PI/360))/(Math.PI/180)*20037508.34/180;
    var b=30;
    var bbox=(x-b)+','+(y-b)+','+(x+b)+','+(y+b);

    var url='https://api.vworld.kr/req/wfs?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=lp_pa_cbnd_bubun&BBOX='+bbox+'&SRSNAME=EPSG:900913&OUTPUT=application/json&KEY='+VWORLD_KEY+'&DOMAIN=c820131-bit.github.io';

    fetch(url).then(r=>r.json()).then(data=>{
        if(!data.features||data.features.length===0){alert('필지 정보 없음');return;}

        var best=null,minD=Infinity;
        data.features.forEach(f=>{
            if(!f.geometry||!f.geometry.coordinates)return;
            var cs=f.geometry.coordinates[0];
            var cx=0,cy=0;
            cs.forEach(c=>{cx+=c[0];cy+=c[1];});
            cx/=cs.length;cy/=cs.length;
            var d=Math.sqrt((cx-x)*(cx-x)+(cy-y)*(cy-y));
            if(d<minD){minD=d;best=f;}
        });

        if(!best)return;
        if(currentPolygon){currentPolygon.setMap(null);}

        var path=best.geometry.coordinates[0].map(c=>{
            var lon=c[0]*180/20037508.34;
            var lat=Math.atan(Math.exp(c[1]*Math.PI/20037508.34))*360/Math.PI-90;
            return new kakao.maps.LatLng(lat,lon);
        });

        var color=type==='inside'?'#4CAF50':type==='nearby'?'#FF9800':'#9E9E9E';
        currentPolygon=new kakao.maps.Polygon({
            path:path,
            strokeWeight:3,
            strokeColor:'#000',
            strokeOpacity:0.8,
            fillColor:color,
            fillOpacity:0.5,
            map:map
        });
    }).catch(e=>{console.error(e);alert('API 오류');});
}
'''

# closeRoadview 함수 찾아서 그 뒤에 삽입
pattern = r"function closeRoadview\(\)\{[^}]+\}"
match = re.search(pattern, content)
if match:
    content = content[:match.end()] + parcel_code + content[match.end():]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("완료!")
print("- 마커 크기: 8~14px")
print("- 클릭 시 폴리곤 표시")
print("- 기타(3만건) 기본 숨김으로 성능 OK")
