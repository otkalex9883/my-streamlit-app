import streamlit as st
import datetime
import io
import os
import re
import sys
import locale

# --- 한글 달력 및 요일을 위한 locale 설정 ---
try:
    locale.setlocale(locale.LC_TIME, 'ko_KR.UTF-8')
except locale.Error:
    pass  # 환경에 한글 Locale이 없을 때는 무시

# --- 구글 Vision 서비스 계정 키파일 환경설정 ---
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in st.secrets:
    key_path = "/tmp/gcpkey.json"
    with open(key_path, "w") as f:
        f.write(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
else:
    st.error("GOOGLE_APPLICATION_CREDENTIALS_JSON가 secrets에 없습니다!")

from google.cloud import vision
from PIL import Image, ImageDraw  # ------ 추가

product_db = {
    "LIGHT&JOY_당을줄인 김천자두쨈 290G": 12,
    "LIGHT&JOY_당을줄인 논산딸기쨈 290G": 12,
    "LIGHT&JOY_당을줄인 논산딸기쨈 480G": 12,
    "LIGHT&JOY_당을줄인 청송사과쨈 290G": 12,
    "LIGHT&JOY 당을줄인 트리플베리쨈 280G": 12,
    "LIGHT&JOY 당을줄인 파인애플망고쨈 280G": 12,
    "간장찜닭양념 240G": 18,
    "간장찜닭양념 480G": 18,
    "갈비양념(호주) 240G": 18,
    "검시럽(롯데리아) 11G": 9,
    "닭볶음탕양념 235G": 18,
    "닭볶음탕양념 470G": 18,
    "돼지갈비양념 240G": 18,
    "돼지갈비양념 480G": 18,
    "돼지갈비양념(미국) 480G": 18,
    "돼지불고기양념 245G": 18,
    "돼지불고기양념 500G": 18,
    "돼지불고기양념(미국) 500G": 18,
    "딸기버터쨈 280G": 10,
    "딸기잼(스타벅스) 12G": 6,
    "딸기잼(에그드랍) 12G": 6,
    "딸기쨈 10KG": 4,
    "딸기쨈 300G": 24,
    "딸기쨈 500G": 24,
    "딸기쨈 850G": 24,
    "딸기쨈(엔제리너스커피) 12G": 6,
    "딸기쨈디스펜팩(KFC) 12G": 6,
    "딸기토핑(맥도날드) 1KG": 6,
    "맛있는딸기쨈830g": 24,
    "맥도날드_스위트앤사워소스(대만R) 28G": 4,
    "메이플시럽(제이앤이) 1KG": 12,
    "믹스피클(제너시스) 3KG": 3,
    "믹스피클(프레시지) 3KG": 4,
    "불고기양념(호주) 240G": 18,
    "블루베리쨈 300G": 24,
    "블루베리쨈 500G": 24,
    "사과쨈 300G": 24,
    "사과쨈 500G": 24,
    "소갈비양념 240G": 18,
    "소갈비양념 480G": 18,
    "소불고기양념 240G": 18,
    "소불고기양념 480G": 18,
    "스위트앤젤_밀감(18입) 90G": 6,
    "스위트앤젤_복숭아(18입) 90G": 6,
    "스위트앤젤_파인(18입) 90G": 6,
    "스위트오이피클 3KG": 12,
    "아삭 오이 피클 240G": 6,
    "아삭 오이 피클 420G": 6,
    "아삭 오이&무 피클 240G": 6,
    "아삭 오이&무 피클 420G": 6,
    "앙버터쨈 280G": 10,
    "오늘의샐러드_코울슬로 100G": 1,
    "오늘의샐러드_콘샐러드 100G": 1,
    "오뚜기딸기쨈(디스펜팩)(240개입) 12G": 6,
    "오뚜기딸기쨈(디스펜팩)(480개입) 12G": 6,
    "오뚜기일회용딸기쨈 12G": 6,
    "오쉐프_떠먹는샤인머스캣(18입) 90G": 6,
    "오쉐프_떠먹는애플망고 90G": 6,
    "오쉐프_메이플시럽(디스펜팩) 11G": 6,
    "오쉐프_슬라이스오이피클 3KG": 6,
    "오쉐프_오미자믹스피클 3KG": 6,
    "오쉐프_초코소스(디스펜팩) 12G": 6,
    "제주담음_제주청귤마말레이드_280G": 12,
    "제주담음_제주한라봉마말레이드_300G_S": 24,
    "코울슬로(맥도날드) 100G": 1,
    "코울슬로(파파존스) 100G": 1,
    "코울슬로(프랭크버거) 100G": 1,
    "코울슬로(피자헛) 100G": 1,
    "콘샐러드(맘스터치) 100G": 1,
    "콘샐러드(파파존스) 100G": 1,
    "콘샐러드(프랭크버거) 100G": 1,
    "콘샐러드(피자헛) 100G": 1,
    "포도쨈 300G": 24,
    "포도쨈 500G": 24,
    "프레스코_파스타소스 토마토 600G": 12,
    "한컵코울슬로 100G": 1,
    "한컵콘샐러드 100G": 1,
    "후레쉬오이피클(쏘렌토) 3KG": 3,
    "후루츠쨈 300G": 24,
    "후루츠쨈 500G": 24,
    "후루츠쨈 850G": 24
}

st.markdown(
    """
    <style>
    .main {background-color: #fff;}
    div.stTextInput > label, div.stDateInput > label {font-weight: bold;}
    input[data-testid="stTextInput"] {background-color: #eee;}
    .yellow-button button {
      background-color: #FFD600 !important;
      color: black !important;
      font-weight: bold;
    }
    .title {font-size:36px; font-weight:bold;}
    .big-blue {font-size:36px; font-weight:bold; color:#1976D2;}
    .big-red {font-size:36px; font-weight:bold; color:#d32f2f;}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
        section.main > div {max-width: 390px; min-width: 390px;}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title">AI 일부인 검사기</div>', unsafe_allow_html=True)
st.write("")

# 세션 상태 변수 초기화
if "product_input" not in st.session_state:
    st.session_state.product_input = ""
if "auto_complete_show" not in st.session_state:
    st.session_state.auto_complete_show = False
if "selected_product_name" not in st.session_state:
    st.session_state.selected_product_name = ""
if "reset_triggered" not in st.session_state:
    st.session_state.reset_triggered = False
if "confirm_success" not in st.session_state:
    st.session_state.confirm_success = False
if "target_date_value" not in st.session_state:
    st.session_state.target_date_value = ""
if "ocr_result" not in st.session_state:
    st.session_state.ocr_result = None

def reset_all():
    st.session_state.product_input = ""
    st.session_state.selected_product_name = ""
    st.session_state.date_input = None
    st.session_state.auto_complete_show = False
    st.session_state.reset_triggered = True
    st.session_state.confirm_success = False
    st.session_state.target_date_value = ""
    st.session_state.ocr_result = None

# --- 제품명 입력과 자동완성 ---
st.write("제품명을 입력하세요")

def on_change_input():
    st.session_state.auto_complete_show = True
    st.session_state.selected_product_name = ""

product_input = st.text_input(
    "",
    value=st.session_state.product_input,
    key="product_input",
    on_change=on_change_input
)

input_value = st.session_state.product_input
matching_products = [
    name for name in product_db.keys()
    if input_value.strip() and input_value.strip() in name
]

def select_product(name):
    st.session_state.product_input = name
    st.session_state.selected_product_name = name
    st.session_state.auto_complete_show = False

if input_value.strip() and st.session_state.auto_complete_show:
    st.write("입력한 내용과 일치하는 제품명:")
    st.markdown("""
    <style>
        .scroll-list {
            max-height: 180px;
            overflow-y: auto;
            border:1px solid #ddd;
            padding:5px;
            margin-bottom:5px;
        }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="scroll-list">', unsafe_allow_html=True)
    for name in matching_products:
        col1, col2 = st.columns([8, 1])
        col1.button(
            name,
            key=f"btn_{name}",
            on_click=select_product,
            args=(name,),
            use_container_width=True
        )
        col2.write("")
    st.markdown('</div>', unsafe_allow_html=True)
elif not input_value.strip():
    st.session_state.selected_product_name = ""
    st.session_state.auto_complete_show = False

# --- 제조일자 입력 ---
st.write("제조일자")
date_input = st.date_input(
    "",
    key="date_input",
    format="YYYY.MM.DD"
)

col1, col2 = st.columns([1, 1])
confirm = col1.button("확인", key="confirm", help="제품명과 제조일자를 확인합니다.", use_container_width=True)
reset = col2.button("새로고침", key="reset", on_click=reset_all, use_container_width=True)

def is_leap_year(year):
    return (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))

def get_last_day(year, month):
    if month in [1,3,5,7,8,10,12]: return 31
    elif month in [4,6,9,11]: return 30
    elif month == 2: return 29 if is_leap_year(year) else 28
    else: return 30

def get_target_date(start_date, months):
    y, m, d = start_date.year, start_date.month, start_date.day
    new_month = m + months
    new_year = y + (new_month - 1) // 12
    new_month = ((new_month - 1) % 12) + 1
    last_day = get_last_day(new_year, new_month)
    if d <= last_day:
        if d == 1:
            return datetime.date(new_year, new_month, 1)
        else:
            return datetime.date(new_year, new_month, d-1)
    else:
        return datetime.date(new_year, new_month, last_day)

if confirm:
    pname = st.session_state.product_input
    dt = st.session_state.date_input

    if pname not in product_db.keys():
        st.warning("제품명을 정확하게 입력하거나 목록에서 선택하세요.")
        st.session_state.confirm_success = False
    elif dt is None:
        st.warning("제조일자를 입력하세요.")
        st.session_state.confirm_success = False
    else:
        months = product_db[pname]
        target_date = get_target_date(dt, months)
        st.session_state.target_date_value = target_date.strftime('%Y.%m.%d')
        st.session_state.confirm_success = True
        st.session_state.ocr_result = None  # OCR 결과 초기화
        st.success(
            f"목표일부인: {target_date.strftime('%Y.%m.%d')}",
            icon="✅"
        )
        st.write(f"제품명: {pname}")
        st.write(f"제조일자: {dt.strftime('%Y.%m.%d')}")
        st.write(f"소비기한(개월): {months}")

if reset:
    st.experimental_rerun()

# --------- OCR 업로드 UI (목표 일부인 출력 이후에만 활성화) ---------
if st.session_state.confirm_success:
    st.markdown("---")
    st.write("## 📸 소비기한 OCR 판독")
    uploaded_file = st.file_uploader(
        "사진을 업로드하거나, 직접 촬영하세요.",
        type=["png","jpg","jpeg","bmp","webp","heic","heif","tiff","tif","gif","pdf"],
        accept_multiple_files=False,
        key="ocr_upload"
    )

    def detect_expiry_with_ocr(image_stream):
        """
        구글 클라우드 Vision으로 이미지 OCR, 텍스트 추출 후
        소비기한(0000.00.00·/·- 형태)만 뽑아내는 함수.

        - '소비기한/유통기한/EXP' 등 키워드로 먼저 탐색
        - 없으면 텍스트 내 가장 처음 패턴 추출
        - 날짜 구분자가 /, - 이여도 .으로 모두 변환, 한글/영어 형태 지원
        - ----- 반환값에 bounding box 정보 포함 (O)
        """
        client = vision.ImageAnnotatorClient()
        content = image_stream.read()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if not texts:
            return None, None, None

        # OCR 전체 텍스트
        full_text = texts[0].description.replace('\n', ' ').replace('\r', ' ')

        # 날짜 패턴 목록 (정규표현식)
        patterns = [
            r"(소비기한|유통기한|EXP(iry)?\s*[:\s\-]?\s*)(\d{4}\.\d{2}\.\d{2})",
            r"(소비기한|유통기한|EXP(iry)?\s*[:\s\-]?\s*)(\d{4}/\d{2}/\d{2})",
            r"(소비기한|유통기한|EXP(iry)?\s*[:\s\-]?\s*)(\d{4}\-\d{2}\-\d{2})"
        ]
        # 텍스트 annotation에서 개별 단어별로 bounding box 포함되어 있음
        # texts[0]=전체, texts[1:]=각 단어별

        # 키워드와 함께 인식된 날짜 패턴의 날짜 부분을 찾아보자
        expiry_date_str = None
        matched_txt = None
        bbox = None

        for patt in patterns:
            match = re.search(patt, full_text)
            if match:
                date_str = match.group(3).replace('/', '.').replace('-', '.')
                expiry_date_str = date_str
                matched_txt = match.group(3)
                break

        if expiry_date_str is None:
            # 키워드 기반이 없으면, 전체 텍스트에서 맨앞 포맷을 추출
            all_date = re.findall(r"\d{4}[./-]\d{2}[./-]\d{2}", full_text)
            if all_date:
                normalized = all_date[0].replace('/', '.').replace('-', '.')
                expiry_date_str = normalized
                matched_txt = all_date[0]

        # bbox는 texts[1:]의 description이 실제 텍스트 단위(단어, 숫자)와 일치
        if expiry_date_str and matched_txt:
            # texts[1:]에서 matched_txt와 같은 description을 최대한 정확히 찾아야 함
            # matched_txt와 완전히 일치하는 description이 있으면 그 bbox를 씀
            candidates = []
            for t in texts[1:]:
                t_desc = t.description
                if t_desc == matched_txt:
                    bbox = t.bounding_poly.vertices
                    break
                # 날짜가 공백 없이 써져 있지 않은 경우 분해된 블럭 여러 개일 수 있음
                # ex) "2023.12.31" → [2023, ., 12, ., 31]
                # 그러면 여러 description을 더해가며 일치하는지 검사
            if not bbox:
                all_texts = [t.description for t in texts[1:]]
                # 날짜 형태의 구성요소 모으기
                date_clean = re.sub(r"[./-]", " ", matched_txt)
                target_parts = date_clean.split()
                idx = 0
                while idx <= len(all_texts) - len(target_parts):
                    window = all_texts[idx:idx+len(target_parts)]
                    join_window = "".join(window)
                    join_target = "".join(target_parts)
                    if join_window == join_target:
                        # bbox는 window 구간 전체의 bbox를 합친 외접 사각형
                        verts = []
                        for i in range(idx, idx+len(target_parts)):
                            verts.extend([
                                (v.x, v.y) for v in texts[i+1].bounding_poly.vertices
                            ])
                        xs = [v[0] for v in verts]
                        ys = [v[1] for v in verts]
                        minx, maxx = min(xs), max(xs)
                        miny, maxy = min(ys), max(ys)
                        bbox = [
                            type(texts[1].bounding_poly.vertices[0])(x=minx, y=miny),
                            type(texts[1].bounding_poly.vertices[0])(x=maxx, y=miny),
                            type(texts[1].bounding_poly.vertices[0])(x=maxx, y=maxy),
                            type(texts[1].bounding_poly.vertices[0])(x=minx, y=maxy)
                        ]
                        break
                    idx += 1
            # 못 찾은 경우 None

        return expiry_date_str, full_text, bbox

    # 업로드 파일이 있으면 OCR 수행
    if uploaded_file is not None:
        # 이미지는 파일로부터 메모리 버퍼를 얻어서 다시 읽어와야 함
        uploaded_file.seek(0)
        raw_image = Image.open(uploaded_file).convert("RGB")
        uploaded_file.seek(0)

        expiry, ocr_fulltext, bbox = detect_expiry_with_ocr(uploaded_file)
        st.session_state.ocr_result = expiry

        if expiry:
            st.info(f"OCR 소비기한: {expiry}")
            if bbox:
                # 빨간색 네모 박스 그리기
                img_copy = raw_image.copy()
                draw = ImageDraw.Draw(img_copy)
                # bbox는 4개 꼭짓점, [(x1, y1), (x2, y2), ...]
                box = [(v.x, v.y) for v in bbox]
                draw.line(box + [box[0]], fill=(255,0,0), width=5)
                # 적당히 리사이즈 (넓이 380px 맞춤)
                max_width = 380
                w, h = img_copy.size
                if w > max_width:
                    scale = max_width / w
                    img_copy = img_copy.resize((int(w*scale), int(h*scale)))
                st.image(img_copy, caption="인식된 소비기한 영역", use_column_width=True)
            if expiry == st.session_state.target_date_value:
                st.markdown(
                    f'<div class="big-blue">일치</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="big-red">불일치</div>',
                    unsafe_allow_html=True
                )
                st.write(f"목표일부인: {st.session_state.target_date_value}")
        else:
            st.error("일부인이 인식되지 않습니다.\n\n(사진 재촬영이나 명확한 부분으로 다시 시도해 주세요.)")
            st.session_state.ocr_result = None
