# -*- coding: utf-8 -*-
import re

# 브이월드 API 키
VWORLD_API_KEY = "D0F229B6-968D-3F5F-B4EB-E509962F466C"

# 추가할 필지 폴리곤 관련 코드
PARCEL_POLYGON_CODE = '''
// 브이월드 API 필지 경계 기능
var VWORLD_API_KEY = "''' + VWORLD_API_KEY + '''";
var currentParcelPolygon = null;
var parcelPolygonsCache = {};

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

// 필지 경계 가져오기
function fetchParcelBoundary(lat, lng, callback) {
    var cacheKey = lat.toFixed(6) + '_' + lng.toFixed(6);
    if (parcelPolygonsCache[cacheKey]) {
        callback(parcelPolygonsCache[cacheKey]);
        return;
    }

    var coords = wgs84ToEpsg3857(lng, lat);
    var buffer = 50; // 50m 버퍼
    var bbox = (coords[0] - buffer) + ',' + (coords[1] - buffer) + ',' + (coords[0] + buffer) + ',' + (coords[1] + buffer);

    var url = 'https://api.vworld.kr/req/wfs?' +
        'SERVICE=WFS&REQUEST=GetFeature&TYPENAME=lp_pa_cbnd_bubun&' +
        'BBOX=' + bbox + '&SRSNAME=EPSG:900913&OUTPUT=application/json&' +
        'KEY=' + VWORLD_API_KEY + '&DOMAIN=c820131-bit.github.io';

    fetch(url)
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (data.features && data.features.length > 0) {
                // 클릭한 좌표와 가장 가까운 필지 찾기
                var clickPoint = coords;
                var closestFeature = null;
                var minDist = Infinity;

                data.features.forEach(function(feature) {
                    if (feature.geometry && feature.geometry.coordinates) {
                        var centroid = getPolygonCentroid(feature.geometry.coordinates[0]);
                        var dist = Math.sqrt(Math.pow(centroid[0] - clickPoint[0], 2) + Math.pow(centroid[1] - clickPoint[1], 2));
                        if (dist < minDist) {
                            minDist = dist;
                            closestFeature = feature;
                        }
                    }
                });

                if (closestFeature) {
                    parcelPolygonsCache[cacheKey] = closestFeature;
                    callback(closestFeature);
                } else {
                    callback(null);
                }
            } else {
                callback(null);
            }
        })
        .catch(function(err) {
            console.error('필지 경계 조회 실패:', err);
            callback(null);
        });
}

// 폴리곤 중심점 계산
function getPolygonCentroid(coords) {
    var x = 0, y = 0, n = coords.length;
    coords.forEach(function(c) { x += c[0]; y += c[1]; });
    return [x / n, y / n];
}

// 필지 폴리곤 표시
function showParcelPolygon(feature, markerData) {
    // 기존 폴리곤 제거
    if (currentParcelPolygon) {
        currentParcelPolygon.setMap(null);
    }

    if (!feature || !feature.geometry || !feature.geometry.coordinates) {
        return;
    }

    // EPSG:3857 좌표를 WGS84로 변환하여 카카오맵 LatLng로 변환
    var path = feature.geometry.coordinates[0].map(function(coord) {
        var wgs = epsg3857ToWgs84(coord[0], coord[1]);
        return new kakao.maps.LatLng(wgs[1], wgs[0]);
    });

    // 폴리곤 색상 (지구내: 녹색, 근처: 주황색, 기타: 회색)
    var fillColor = '#4CAF50';
    var strokeColor = '#2E7D32';
    if (markerData && markerData.layer) {
        if (markerData.layer === 'nearby') {
            fillColor = '#FF9800';
            strokeColor = '#E65100';
        } else if (markerData.layer === 'other') {
            fillColor = '#9E9E9E';
            strokeColor = '#616161';
        }
    }

    currentParcelPolygon = new kakao.maps.Polygon({
        path: path,
        strokeWeight: 3,
        strokeColor: strokeColor,
        strokeOpacity: 1,
        fillColor: fillColor,
        fillOpacity: 0.35,
        map: map
    });

    // 필지 정보 인포윈도우
    if (feature.properties) {
        var pnu = feature.properties.pnu || '';
        var jibun = feature.properties.jibun || '';
        var jimok = feature.properties.jimok || '';
    }
}

// 폴리곤 숨기기
function hideParcelPolygon() {
    if (currentParcelPolygon) {
        currentParcelPolygon.setMap(null);
        currentParcelPolygon = null;
    }
}
'''

# index.html 파일 읽기
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. closeRoadview 함수 다음에 필지 폴리곤 코드 삽입
insert_point = "function closeRoadview(){\ndocument.getElementById('roadview').style.display='none';\ndocument.getElementById('btnRoadview').classList.remove('active');\n}"
if insert_point in content:
    content = content.replace(insert_point, insert_point + PARCEL_POLYGON_CODE)
else:
    # 다른 방식으로 삽입 위치 찾기
    pattern = r"function closeRoadview\(\)\{[^}]+\}"
    match = re.search(pattern, content)
    if match:
        content = content[:match.end()] + PARCEL_POLYGON_CODE + content[match.end():]

# 2. addAuctions 함수에 클릭 이벤트 추가
# 기존: kakao.maps.event.addListener(m,'mouseout',function(){info.close()});
# 추가: kakao.maps.event.addListener(m,'click',function(){...});
old_mouseout = "kakao.maps.event.addListener(m,'mouseout',function(){info.close()});\nm.data=a;"
new_mouseout = """kakao.maps.event.addListener(m,'mouseout',function(){info.close()});
kakao.maps.event.addListener(m,'click',function(){
    fetchParcelBoundary(a.lat, a.lng, function(feature) {
        showParcelPolygon(feature, {layer: name});
    });
    map.setCenter(new kakao.maps.LatLng(a.lat, a.lng));
    map.setLevel(2);
});
m.data=a;"""

if old_mouseout in content:
    content = content.replace(old_mouseout, new_mouseout)
else:
    # 다른 방식으로 찾기
    old_pattern = r"kakao\.maps\.event\.addListener\(m,'mouseout',function\(\)\{info\.close\(\)\}\);\s*m\.data=a;"
    new_text = """kakao.maps.event.addListener(m,'mouseout',function(){info.close()});
kakao.maps.event.addListener(m,'click',function(){
    fetchParcelBoundary(a.lat, a.lng, function(feature) {
        showParcelPolygon(feature, {layer: name});
    });
    map.setCenter(new kakao.maps.LatLng(a.lat, a.lng));
    map.setLevel(2);
});
m.data=a;"""
    content = re.sub(old_pattern, new_text, content)

# 3. 지도 클릭 시 폴리곤 숨기기 이벤트 추가 (init 함수 내에)
old_init = "toggle('other');  // 기타는 기본 숨김\n}"
new_init = """toggle('other');  // 기타는 기본 숨김
kakao.maps.event.addListener(map,'click',function(){hideParcelPolygon();});
}"""

if old_init in content:
    content = content.replace(old_init, new_init)

# 파일 저장
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("index.html 파일이 성공적으로 수정되었습니다!")
print("- 브이월드 WFS API를 사용한 필지 경계 표시 기능 추가")
print("- 마커 클릭 시 해당 필지의 폴리곤 표시")
print("- 지도 빈 공간 클릭 시 폴리곤 숨김")
