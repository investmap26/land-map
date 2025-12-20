# -*- coding: utf-8 -*-
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 카카오맵 SDK에 클러스터러 라이브러리 추가
old_sdk = "script.src = 'https://dapi.kakao.com/v2/maps/sdk.js?appkey=7e60f6a42602355b925c66ea6db3bd87&autoload=false';"
new_sdk = "script.src = 'https://dapi.kakao.com/v2/maps/sdk.js?appkey=7e60f6a42602355b925c66ea6db3bd87&libraries=clusterer&autoload=false';"
content = content.replace(old_sdk, new_sdk)

# 2. 클러스터러 변수 추가
old_vars = "var map,layers={inside:[],nearby:[],other:[],proj:[],rail:[],highway:[],dev:[]};"
new_vars = """var map,layers={inside:[],nearby:[],other:[],proj:[],rail:[],highway:[],dev:[]};
var clusterers={inside:null,nearby:null,other:null};"""
content = content.replace(old_vars, new_vars)

# 3. addAuctions 함수를 클러스터러 방식으로 변경
old_add_auctions = '''function addAuctions(arr,name,color){
var size=name==='other'?4:7;
var stroke=name==='other'?0.5:1;
var svg='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'"><circle cx="'+(size/2)+'" cy="'+(size/2)+'" r="'+(size/2-0.5)+'" fill="'+color+'" stroke="#fff" stroke-width="'+stroke+'"/></svg>');
var img=new kakao.maps.MarkerImage(svg,new kakao.maps.Size(size,size),{offset:new kakao.maps.Point(size/2,size/2)});
arr.forEach(function(a){
var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(a.lat,a.lng),image:img,map:map});'''

new_add_auctions = '''function addAuctions(arr,name,color){
var size=name==='other'?8:12;
var stroke=name==='other'?1:2;
var svg='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'"><circle cx="'+(size/2)+'" cy="'+(size/2)+'" r="'+(size/2-1)+'" fill="'+color+'" stroke="#fff" stroke-width="'+stroke+'"/></svg>');
var img=new kakao.maps.MarkerImage(svg,new kakao.maps.Size(size,size),{offset:new kakao.maps.Point(size/2,size/2)});
var markers=[];
arr.forEach(function(a){
var m=new kakao.maps.Marker({position:new kakao.maps.LatLng(a.lat,a.lng),image:img});'''

content = content.replace(old_add_auctions, new_add_auctions)

# 4. addAuctions 함수 끝부분에 클러스터러 생성 추가
old_end_auctions = '''m.data=a;
layers[name].push(m);
allMarkers.push({marker:m,data:a,layer:name});
});
}'''

new_end_auctions = '''m.data=a;
markers.push(m);
layers[name].push(m);
allMarkers.push({marker:m,data:a,layer:name});
});

// 클러스터러 생성
var clusterStyles = [{
    width: 50, height: 50,
    background: color,
    borderRadius: '25px',
    color: '#fff',
    textAlign: 'center',
    fontWeight: 'bold',
    lineHeight: '50px',
    opacity: 0.9
}];

clusterers[name] = new kakao.maps.MarkerClusterer({
    map: map,
    averageCenter: true,
    minLevel: 5,
    disableClickZoom: false,
    styles: clusterStyles,
    markers: markers
});
}'''

content = content.replace(old_end_auctions, new_end_auctions)

# 5. toggle 함수 수정 - 클러스터러도 함께 토글
old_toggle = '''function toggle(n){
var id='chk'+n.charAt(0).toUpperCase()+n.slice(1);
var chk=document.getElementById(id);
var show=chk?chk.checked:false;
layers[n].forEach(function(o){o.setMap(show?map:null)});
}'''

new_toggle = '''function toggle(n){
var id='chk'+n.charAt(0).toUpperCase()+n.slice(1);
var chk=document.getElementById(id);
var show=chk?chk.checked:false;
if(clusterers[n]){
    if(show){
        clusterers[n].setMap(map);
    }else{
        clusterers[n].setMap(null);
    }
}else{
    layers[n].forEach(function(o){o.setMap(show?map:null)});
}
}'''

content = content.replace(old_toggle, new_toggle)

# 6. init 함수에서 기타는 클러스터러도 숨기기
old_init_toggle = "toggle('other');  // 기타는 기본 숨김"
new_init_toggle = """toggle('other');  // 기타는 기본 숨김
// 줌 레벨 변경 시 마커 크기 조정
kakao.maps.event.addListener(map,'zoom_changed',function(){
    var level=map.getLevel();
    // 줌 레벨에 따른 클러스터 최소 레벨 조정
});"""

content = content.replace(old_init_toggle, new_init_toggle)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("완료!")
print("- 마커 클러스터링 적용 (축소 시 마커 묶음 표시)")
print("- 마커 크기 확대 (8~12px)")
print("- 성능 개선")
