# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. toggle 함수에서 other를 auction, public으로 변경
old_toggle_check = "if(n==='inside'||n==='nearby'||n==='other'){"
new_toggle_check = "if(n==='inside'||n==='nearby'||n==='auction'||n==='public'){"
content = content.replace(old_toggle_check, new_toggle_check)

# 2. showParcel 함수에서 색상 처리 수정
old_color = "var col=type==='inside'?'#4CAF50':type==='nearby'?'#FF9800':'#9E9E9E';"
new_color = "var col=type==='inside'?'#4CAF50':type==='nearby'?'#FF9800':type==='auction'?'#2196F3':type==='public'?'#9C27B0':'#9E9E9E';"
content = content.replace(old_color, new_color)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("완료!")
print("- toggle 함수에서 auction/public 처리 추가")
print("- 폴리곤 색상 설정 수정")
