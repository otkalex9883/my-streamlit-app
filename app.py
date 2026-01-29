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

product_db = {
    "아삭 오이 피클": 6,
    "아삭 오이&무 피클": 6,
    "스위트 오이피클": 12,
    "오'쉐프 슬라이스 오이피클": 6,
    "오'쉐프 오미자 믹스피클": 6,
    "쏘렌토 후레쉬 오이피클": 3,
    "믹스피클(제너시스)": 3,
    "믹스피클(프레시지)": 4,
    "오뚜기 딸기쨈 (일회용)": 6,
    "맥도날드 딸기토핑": 6,
    "딸기쨈": 24,
    "딸기잼(10kg 캔)": 4,
    "맛있는 딸기잼": 24,
    "후루츠쨈": 24,
    "포도쨈": 24,
    "사과쨈": 24,
    "블루베리쨈": 24,
    "제주한라봉마말레이드": 24,
    "LIGHT&JOY 당을 줄인 논산딸기쨈": 12,
    "LIGHT&JOY 당을 줄인 김천자두쨈": 12,
    "LIGHT&JOY 당을 줄인 청송사과쨈": 12,
    "애플시나몬쨈(트레이더스)": 18,
    "Light Sugar 딸기쨈(조흥)": 3,
    "Light Sugar 사과쨈(조흥)": 3,
    "제주청귤마말레이드": 12,
    "메이플시럽(제이앤이)": 12,
    "딸기버터쨈": 10,
    "앙버터쨈": 10,
    "돼지불고기양념": 18,
    "돼지갈비양념": 18,
    "소불고기양념": 18,
    "소갈비양념": 18,
    "간장찜닭양념": 18,
    "닭볶음탕양념": 18,
    "프레스코 토마토 파스타소스": 12,
    "검시럽(롯데리아)": 9,
    "오쉐프 메이플시럽 디스펜팩": 6,
    "오'쉐프 초코 소스": 6,
    "오뚜기 딸기쨈 (디스펜팩)": 6,
    "KFC 딸기쨈 (디스펜팩)": 6,
    "엔제리너스 딸기쨈 (디스펜팩)": 6,
    "에그드랍 딸기잼": 6,
    "딸기잼(스타벅스)": 6,
    "스위트앤사워소스(대만 맥도날드)": 4,
    "스위트앤젤 복숭아": 6,
    "스위트앤젤 파인": 6,
    "스위트앤젤 밀감": 6,
    "피코크젤리 복숭아": 6,
    "피코크젤리 망고": 6,
    "피코크젤리 포도": 6,
    "오'쉐프 떠먹는 샤인머스캣": 6,
    "오'쉐프 떠먹는 애플망고": 6,
    "콘샐러드(뉴욕버거)": 1,
    "오늘의 샐러드 콘샐러드": 1,
    "콘샐러드(파파존스)": 1,
    "콘샐러드(프랭크버거)": 1,
    "콘샐러드(피자헛)": 1,
    "콘샐러드(맘스터치)": 1,
    "오늘의 샐러드 코울슬로": 1,
    "코울슬로(맥도날드)": 1,
    "코울슬로(파파존스)": 1,
    "코울슬로(프랭크버거)": 1,
    "코울슬로(피자헛)": 1,
    "한컵 콘샐러드": 1,
    "한컵 코울슬로": 1
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
        """
        client = vision.ImageAnnotatorClient()
        content = image_stream.read()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if not texts:
            return None, None

        # OCR 전체 텍스트
        full_text = texts[0].description.replace('\n', ' ').replace('\r', ' ')

        # '소비기한' 주변 0000.00.00, 혹은 날짜만 추출
        patterns = [
            r"(소비기한|유통기한|EXP(iry)?\s*[:\s\-]?\s*)(\d{4}\.\d{2}\.\d{2})",
            r"(소비기한|유통기한|EXP(iry)?\s*[:\s\-]?\s*)(\d{4}/\d{2}/\d{2})",
            r"(소비기한|유통기한|EXP(iry)?\s*[:\s\-]?\s*)(\d{4}\-\d{2}\-\d{2})"
        ]
        for patt in patterns:
            match = re.search(patt, full_text)
            if match:
                date_str = match.group(3).replace('/', '.').replace('-', '.')
                return date_str, full_text

        # 모든 패턴 중 제일 처음 것 하나 추출
        all_date = re.findall(r"\d{4}[./-]\d{2}[./-]\d{2}", full_text)
        if all_date:
            normalized = all_date[0].replace('/', '.').replace('-', '.')
            return normalized, full_text

        return None, full_text

    # 업로드 파일이 있으면 OCR 수행
    if uploaded_file is not None:
        expiry, ocr_fulltext = detect_expiry_with_ocr(uploaded_file)
        st.session_state.ocr_result = expiry

        if expiry:
            st.info(f"OCR 소비기한: {expiry}")
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
