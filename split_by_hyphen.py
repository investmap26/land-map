# -*- coding: utf-8 -*-
import re
import json

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# other 배열에서 경매/공매 분류
match = re.search(r'var other=(\[[\s\S]*?\]);', content)
if match:
    data = json.loads(match.group(1))

    auction = []  # 경매 (하이픈 1개)
    public_sale = []  # 공매 (하이픈 2개 이상)

    for item in data:
        case_no = item.get('case_no', '')
        # 괄호 제거 후 하이픈 개수 확인
        clean_case = case_no.split('(')[0]  # 괄호 앞부분만
        hyphen_count = clean_case.count('-')

        if hyphen_count >= 2:
            public_sale.append(item)
        else:
            auction.append(item)

    print(f"경매 (하이픈 1개): {len(auction)}개")
    print(f"공매 (하이픈 2개+): {len(public_sale)}개")

    # 샘플 확인
    print("\n경매 샘플:")
    for item in auction[:5]:
        print(f"  {item['case_no']}")

    print("\n공매 샘플:")
    for item in public_sale[:5]:
        print(f"  {item['case_no']}")

    # ========== HTML 수정 ==========

    # 1. 기존 other 배열을 auction과 public_sale로 분리
    auction_json = json.dumps(auction, ensure_ascii=False)
    public_json = json.dumps(public_sale, ensure_ascii=False)

    # 2. 변수 선언 수정
    old_vars = '''var auctionData={inside:[],nearby:[],other:[]};
var displayedMarkers=[];
var showAuction={inside:false,nearby:false,other:false};'''

    new_vars = '''var auctionData={inside:[],nearby:[],auction:[],public:[]};
var displayedMarkers=[];
var showAuction={inside:false,nearby:false,auction:false,public:false};'''

    content = content.replace(old_vars, new_vars)

    # 3. other 변수를 auction과 public으로 분리
    # 기존 other= 찾아서 수정
    other_match = re.search(r'var other=\[[\s\S]*?\];', content)
    if other_match:
        old_other = other_match.group(0)
        new_vars_decl = f'var auction_data={auction_json};\nvar public_data={public_json};'
        content = content.replace(old_other, new_vars_decl)

    # 4. addAuctions 호출 수정
    content = content.replace(
        "addAuctions(other,'other','#9E9E9E');",
        "addAuctions(auction_data,'auction','#2196F3');\naddAuctions(public_data,'public','#9C27B0');"
    )

    # 5. HTML 체크박스 수정
    old_checkbox = '''<div class="row"><input type="checkbox" id="chkOther" onchange="toggle('other')"><span style="font-size:16px">⚪</span><label>기타 (30687)</label></div>'''

    new_checkbox = f'''<div class="row"><input type="checkbox" id="chkAuction" onchange="toggle('auction')"><span style="font-size:16px">🔵</span><label>경매 ({len(auction)})</label></div>
<div class="row"><input type="checkbox" id="chkPublic" onchange="toggle('public')"><span style="font-size:16px">🟣</span><label>공매 ({len(public_sale)})</label></div>'''

    content = content.replace(old_checkbox, new_checkbox)

    # 6. refreshAuctionMarkers 함수 수정
    content = content.replace(
        "['inside','nearby','other'].forEach(function(name){",
        "['inside','nearby','auction','public'].forEach(function(name){"
    )

    # 7. 색상 설정 수정
    old_size = "var size=name==='other'?10:16;"
    new_size = "var size=(name==='auction'||name==='public')?12:16;"
    content = content.replace(old_size, new_size)

    # 8. init 함수의 레이어 목록 수정
    content = content.replace(
        "['inside','nearby','other','proj','rail','highway','dev'].forEach",
        "['inside','nearby','auction','public','proj','rail','highway','dev'].forEach"
    )

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n완료! 기타를 경매/공매로 분리")
