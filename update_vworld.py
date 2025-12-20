# -*- coding: utf-8 -*-
import re

VWORLD_API_KEY = "D0F229B6-968D-3F5F-B4EB-E509962F466C"

# index.html 파일 읽기
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 기존 카카오맵 지적도 오버레이 관련 코드 제거
# 클릭 핸들러 변경
old_click = """kakao.maps.event.addListener(m,'click',function(){
    showCadastralOverlay(a.lat, a.lng, a);
});"""

new_click = """kakao.maps.event.addListener(m,'click',function(){
    fetchParcelPolygon(a.lat, a.lng, name);
});"""

content = content.replace(old_click, new_click)

# 2. 기존 카카오맵 지적도 코드 제거
cadastral_start = '// 카카오맵 지적도 오버레이 기능'
cadastral_end = '''// 지적도 토글
function toggleCadastral() {
    if (cadastralOverlayOn) {
        hideCadastralOverlay();
    } else {
        map.addOverlayMapTypeId(kakao.maps.MapTypeId.USE_DISTRICT);
        cadastralOverlayOn = true;
        updateCadastralButton(true);
    }
}'''

if cadastral_start in content and cadastral_end in content:
    start_idx = content.find(cadastral_start)
    end_idx = content.find(cadastral_end) + len(cadastral_end)
    content = content[:start_idx] + content[end_idx:]

# 3. 지적도 버튼을 필지경계 버튼으로 변경
old_btn = '''<button id="btnCadastral" onclick="toggleCadastral()" style="margin-top:6px;width:100%">📐 지적도</button>'''
new_btn = '''<button id="btnParcel" onclick="toggleParcelMode()" style="margin-top:6px;width:100%">📐 필지경계</button>'''
content = content.replace(old_btn, new_btn)

# 4. 지도 클릭 이벤트 수정
content = content.replace(
    "kakao.maps.event.addListener(map,'click',function(){hideCadastralOverlay();});",
    "kakao.maps.event.addListener(map,'click',function(){hideParcelPolygon();});"
)

# 5. 브이월드 필지 폴리곤 코드 추가
vworld_code = '''
// 브이월드 WFS API 필지 경계 기능
var VWORLD_API_KEY = "''' + VWORLD_API_KEY + '''";
var currentParcelPolygon = null;
var parcelModeOn = false;

// WGS84 -> EPSG:3857 좌표 변환
function wgs84ToEpsg3857(lng, lat) {
    var x = lng * 20037508.34 / 180;
    var y = Math.log(Math.tan((90 + lat) * Math.PI / 360)) / (Math.PI / 180);
    y = y * 20037508.34 / 180;
    return [x, y];
}

// EPSG:3857 -> WGS84 좌표 변환
function epsg3857ToWgs84(x, y) {
    var lng = x * 180 / 20037508.34;
    var lat = Math.atan(Math.exp(y * Math.PI / 20037508.34)) * 360 / Math.PI - 90;
    return [lng, lat];
}

// 필지 경계 폴리곤 가져오기
function fetchParcelPolygon(lat, lng, layerType) {
    // 해당 위치로 이동 및 확대
    map.setCenter(new kakao.maps.LatLng(lat, lng));
    map.setLevel(2);

    var coords = wgs84ToEpsg3857(lng, lat);
    var buffer = 30;
    var bbox = (coords[0] - buffer) + ',' + (coords[1] - buffer) + ',' + (coords[0] + buffer) + ',' + (coords[1] + buffer);

    var url = 'https://api.vworld.kr/req/wfs?' +
        'SERVICE=WFS&REQUEST=GetFeature&TYPENAME=lp_pa_cbnd_bubun&' +
        'BBOX=' + bbox + '&SRSNAME=EPSG:900913&OUTPUT=application/json&' +
        'KEY=' + VWORLD_API_KEY + '&DOMAIN=c820131-bit.github.io';

    fetch(url)
        .then(function(response) {
            if (!response.ok) throw new Error('API 응답 오류');
            return response.json();
        })
        .then(function(data) {
            if (data.features && data.features.length > 0) {
                var clickPoint = coords;
                var closestFeature = null;
                var minDist = Infinity;

                data.features.forEach(function(feature) {
                    if (feature.geometry && feature.geometry.coordinates) {
                        var rings = feature.geometry.coordinates[0];
                        var cx = 0, cy = 0, n = rings.length;
                        rings.forEach(function(c) { cx += c[0]; cy += c[1]; });
                        cx /= n; cy /= n;
                        var dist = Math.sqrt(Math.pow(cx - clickPoint[0], 2) + Math.pow(cy - clickPoint[1], 2));
                        if (dist < minDist) {
                            minDist = dist;
                            closestFeature = feature;
                        }
                    }
                });

                if (closestFeature) {
                    drawParcelPolygon(closestFeature, layerType);
                }
            } else {
                console.log('필지 데이터 없음');
            }
        })
        .catch(function(err) {
            console.error('필지 조회 실패:', err);
            alert('필지 경계를 가져오지 못했습니다.');
        });
}

// 필지 폴리곤 그리기
function drawParcelPolygon(feature, layerType) {
    hideParcelPolygon();

    if (!feature.geometry || !feature.geometry.coordinates) return;

    var path = feature.geometry.coordinates[0].map(function(coord) {
        var wgs = epsg3857ToWgs84(coord[0], coord[1]);
        return new kakao.maps.LatLng(wgs[1], wgs[0]);
    });

    // 레이어 타입에 따른 색상
    var fillColor = '#4CAF50';
    var strokeColor = '#1B5E20';
    if (layerType === 'nearby') {
        fillColor = '#FF9800';
        strokeColor = '#E65100';
    } else if (layerType === 'other') {
        fillColor = '#9E9E9E';
        strokeColor = '#424242';
    }

    currentParcelPolygon = new kakao.maps.Polygon({
        path: path,
        strokeWeight: 3,
        strokeColor: strokeColor,
        strokeOpacity: 1,
        fillColor: fillColor,
        fillOpacity: 0.5,
        map: map
    });

    // 필지 정보 표시
    if (feature.properties) {
        var pnu = feature.properties.pnu || '';
        var jibun = feature.properties.jibun || '';
        console.log('필지:', pnu, jibun);
    }
}

// 필지 폴리곤 숨기기
function hideParcelPolygon() {
    if (currentParcelPolygon) {
        currentParcelPolygon.setMap(null);
        currentParcelPolygon = null;
    }
}

// 필지경계 모드 토글
function toggleParcelMode() {
    var btn = document.getElementById('btnParcel');
    parcelModeOn = !parcelModeOn;
    if (parcelModeOn) {
        btn.style.background = 'linear-gradient(135deg,#E91E63 0%,#9C27B0 100%)';
        btn.style.color = '#fff';
        alert('마커를 클릭하면 해당 필지 경계가 표시됩니다.');
    } else {
        btn.style.background = '#f0f0f0';
        btn.style.color = '#555';
        hideParcelPolygon();
    }
}
'''

# closeRoadview 함수 다음에 삽입
close_roadview_pattern = r"function closeRoadview\(\)\{[^}]+\}"
match = re.search(close_roadview_pattern, content)
if match:
    content = content[:match.end()] + vworld_code + content[match.end():]

# 파일 저장
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("완료! 브이월드 WFS API로 필지 폴리곤 표시 기능 구현")
print("- 마커 클릭 시 해당 필지만 색칠된 폴리곤 표시")
print("- 지구내: 녹색, 근처: 주황색, 기타: 회색")
