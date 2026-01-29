import streamlit as st
import datetime

product_db =  {
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

# 세션 상태 초기화
if "product_input" not in st.session_state:
    st.session_state.product_input = ""
if "auto_complete_show" not in st.session_state:
    st.session_state.auto_complete_show = False
if "selected_product_name" not in st.session_state:
    st.session_state.selected_product_name = ""
if "reset_triggered" not in st.session_state:
    st.session_state.reset_triggered = False

def reset_all():
    st.session_state.product_input = ""
    st.session_state.selected_product_name = ""
    st.session_state.date_input = None
    st.session_state.auto_complete_show = False
    st.session_state.reset_triggered = True

# --- 제품명 입력 및 자동완성 ---
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

# 자동완성 후보
input_value = st.session_state.product_input
matching_products = [
    name for name in product_db.keys()
    if input_value.strip() and input_value.strip() in name
]

def select_product(name):
    st.session_state.product_input = name         # 입력창에 자동 입력
    st.session_state.selected_product_name = name  # 선택된 제품명
    st.session_state.auto_complete_show = False    # 자동완성창 닫기

# 자동완성창: 무조건 입력창 유지, 창만 숨김/출현 제어
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
    # 입력이 없으면 자동완성창 숨김, 선택도 초기화
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
    elif dt is None:
        st.warning("제조일자를 입력하세요.")
    else:
        months = product_db[pname]
        target_date = get_target_date(dt, months)
        st.success(
            f"목표일부인: {target_date.strftime('%Y.%m.%d')}",
            icon="✅"
        )
        st.write(f"제품명: {pname}")
        st.write(f"제조일자: {dt.strftime('%Y.%m.%d')}")
        st.write(f"소비기한(개월): {months}")

if reset:
    st.experimental_rerun()
