# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 다른 CORS 프록시로 변경
old_url = "var url='https://corsproxy.io/?'+encodeURIComponent('https://api.vworld.kr/req/wfs?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=lp_pa_cbnd_bubun&BBOX='+bbox+'&SRSNAME=EPSG:900913&OUTPUT=application/json&KEY='+VWORLD_KEY);"

new_url = "var url='https://api.allorigins.win/raw?url='+encodeURIComponent('https://api.vworld.kr/req/wfs?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=lp_pa_cbnd_bubun&BBOX='+bbox+'&SRSNAME=EPSG:900913&OUTPUT=application/json&KEY='+VWORLD_KEY);"

content = content.replace(old_url, new_url)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("다른 CORS 프록시로 변경 완료")
