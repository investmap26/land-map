# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Vworld 직접 호출을 Netlify 함수 호출로 변경
old_url = "var url='https://api.vworld.kr/req/wfs?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=lp_pa_cbnd_bubun&BBOX='+bbox+'&SRSNAME=EPSG:900913&OUTPUT=application/json&KEY='+VWORLD_KEY+'&DOMAIN=c820131-bit.github.io';"

new_url = "var url='/.netlify/functions/vworld?bbox='+bbox;"

content = content.replace(old_url, new_url)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Netlify 함수 호출로 변경 완료!")
