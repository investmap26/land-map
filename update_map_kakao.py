# -*- coding: utf-8 -*-
import re

# index.html 파일 읽기
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 기존 브이월드 API 관련 코드 제거 (이전에 추가한 코드)
# fetchParcelBoundary 호출 부분을 새 코드로 교체
old_click_handler = """kakao.maps.event.addListener(m,'click',function(){
    fetchParcelBoundary(a.lat, a.lng, function(feature) {
        showParcelPolygon(feature, {layer: name});
    });
    map.setCenter(new kakao.maps.LatLng(a.lat, a.lng));
    map.setLevel(2);
});"""

new_click_handler = """kakao.maps.event.addListener(m,'click',function(){
    showCadastralOverlay(a.lat, a.lng, a);
});"""

content = content.replace(old_click_handler, new_click_handler)

# 2. 기존 브이월드 관련 함수들 제거
vworld_code_start = '// 브이월드 API 필지 경계 기능'
vworld_code_end = '''// 폴리곤 숨기기
function hideParcelPolygon() {
    if (currentParcelPolygon) {
        currentParcelPolygon.setMap(null);
        currentParcelPolygon = null;
    }
}'''

if vworld_code_start in content and vworld_code_end in content:
    start_idx = content.find(vworld_code_start)
    end_idx = content.find(vworld_code_end) + len(vworld_code_end)
    content = content[:start_idx] + content[end_idx:]

# 3. hideParcelPolygon() 호출을 hideCadastralOverlay()로 변경
content = content.replace("kakao.maps.event.addListener(map,'click',function(){hideParcelPolygon();});",
                          "kakao.maps.event.addListener(map,'click',function(){hideCadastralOverlay();});")

# 4. 새로운 카카오맵 지적도 오버레이 코드 추가
cadastral_code = '''
// 카카오맵 지적도 오버레이 기능
var cadastralOverlayOn = false;
var selectedMarkerInfo = null;

// 지적도 오버레이 표시
function showCadastralOverlay(lat, lng, data) {
    // 지적도 오버레이 켜기
    if (!cadastralOverlayOn) {
        map.addOverlayMapTypeId(kakao.maps.MapTypeId.USE_DISTRICT);
        cadastralOverlayOn = true;
        updateCadastralButton(true);
    }

    // 해당 위치로 이동 및 확대
    map.setCenter(new kakao.maps.LatLng(lat, lng));
    map.setLevel(2);

    // 선택된 마커 정보 저장
    selectedMarkerInfo = data;
}

// 지적도 오버레이 숨기기
function hideCadastralOverlay() {
    if (cadastralOverlayOn) {
        map.removeOverlayMapTypeId(kakao.maps.MapTypeId.USE_DISTRICT);
        cadastralOverlayOn = false;
        updateCadastralButton(false);
    }
    selectedMarkerInfo = null;
}

// 지적도 버튼 상태 업데이트
function updateCadastralButton(active) {
    var btn = document.getElementById('btnCadastral');
    if (btn) {
        if (active) {
            btn.classList.add('active');
            btn.style.background = 'linear-gradient(135deg,#E91E63 0%,#9C27B0 100%)';
        } else {
            btn.classList.remove('active');
            btn.style.background = '#f0f0f0';
            btn.style.color = '#555';
        }
    }
}

// 지적도 토글
function toggleCadastral() {
    if (cadastralOverlayOn) {
        hideCadastralOverlay();
    } else {
        map.addOverlayMapTypeId(kakao.maps.MapTypeId.USE_DISTRICT);
        cadastralOverlayOn = true;
        updateCadastralButton(true);
    }
}
'''

# closeRoadview 함수 다음에 새 코드 삽입
close_roadview_pattern = r"function closeRoadview\(\)\{[^}]+\}"
match = re.search(close_roadview_pattern, content)
if match:
    # 기존에 추가된 빈 공간 정리
    content = content[:match.end()] + cadastral_code + content[match.end():]

# 5. 지적도 버튼 추가 (UI에)
old_map_type_buttons = '<button id="btnRoadview" onclick="toggleRoadview()">🚶 로드뷰</button>'
new_map_type_buttons = '''<button id="btnRoadview" onclick="toggleRoadview()">🚶 로드뷰</button>
<button id="btnCadastral" onclick="toggleCadastral()" style="margin-top:6px;width:100%">📐 지적도</button>'''

content = content.replace(old_map_type_buttons, new_map_type_buttons)

# 6. 지도 클릭 이벤트가 없으면 추가
if "kakao.maps.event.addListener(map,'click'" not in content:
    old_init_end = "toggle('other');  // 기타는 기본 숨김\n}"
    new_init_end = """toggle('other');  // 기타는 기본 숨김
kakao.maps.event.addListener(map,'click',function(){hideCadastralOverlay();});
}"""
    content = content.replace(old_init_end, new_init_end)

# 파일 저장
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("index.html 파일이 성공적으로 수정되었습니다!")
print("- 카카오맵 지적도(USE_DISTRICT) 오버레이 기능 추가")
print("- 마커 클릭 시 지적도 표시 및 해당 위치로 확대")
print("- 지적도 토글 버튼 추가")
print("- 지도 빈 공간 클릭 시 지적도 숨김")
