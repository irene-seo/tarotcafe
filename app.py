import streamlit as st
import os
import base64
import random
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="춘식이의 타로카페",
    page_icon="🔮",
    layout="centered"
)

def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

chunsik_b64 = get_base64_image("chunsik.png.png")

# 카드마다 춘식이 색상 필터 다르게!
TAROT_CARDS = [
    {"name": "바보",        "emoji": "🃏",  "filter": "hue-rotate(0deg) saturate(1)"},
    {"name": "마법사",      "emoji": "🪄",  "filter": "hue-rotate(60deg) saturate(1.5)"},
    {"name": "여사제",      "emoji": "🌙",  "filter": "hue-rotate(240deg) saturate(1.3) brightness(1.1)"},
    {"name": "여황제",      "emoji": "👸",  "filter": "hue-rotate(320deg) saturate(1.8)"},
    {"name": "황제",        "emoji": "👑",  "filter": "sepia(0.6) saturate(2) brightness(1.1)"},
    {"name": "교황",        "emoji": "🕊️", "filter": "hue-rotate(180deg) saturate(1.2) brightness(1.2)"},
    {"name": "연인",        "emoji": "💞",  "filter": "hue-rotate(300deg) saturate(2) brightness(1.1)"},
    {"name": "전차",        "emoji": "🏆",  "filter": "hue-rotate(30deg) saturate(2)"},
    {"name": "힘",          "emoji": "🦁",  "filter": "hue-rotate(15deg) saturate(2.5) brightness(0.9)"},
    {"name": "은둔자",      "emoji": "🕯️", "filter": "grayscale(0.6) brightness(0.8)"},
    {"name": "운명의 바퀴", "emoji": "🎡",  "filter": "hue-rotate(90deg) saturate(1.5)"},
    {"name": "정의",        "emoji": "⚖️", "filter": "hue-rotate(210deg) saturate(1.4)"},
    {"name": "매달린 자",   "emoji": "🙃",  "filter": "hue-rotate(150deg) saturate(1.3)"},
    {"name": "변화",        "emoji": "🦋",  "filter": "hue-rotate(270deg) saturate(1.2) brightness(0.85)"},
    {"name": "절제",        "emoji": "🌊",  "filter": "hue-rotate(190deg) brightness(1.2) saturate(1.3)"},
    {"name": "악마",        "emoji": "🔥",  "filter": "hue-rotate(0deg) saturate(3) brightness(0.75)"},
    {"name": "탑",          "emoji": "⚡",  "filter": "hue-rotate(20deg) saturate(2.5) brightness(0.85)"},
    {"name": "별",          "emoji": "⭐",  "filter": "brightness(1.4) saturate(0.7)"},
    {"name": "달",          "emoji": "🌕",  "filter": "hue-rotate(230deg) saturate(1.5) brightness(1.1)"},
    {"name": "태양",        "emoji": "☀️", "filter": "sepia(0.7) brightness(1.3) saturate(1.8)"},
    {"name": "심판",        "emoji": "📯",  "filter": "hue-rotate(280deg) saturate(1.4)"},
    {"name": "세계",        "emoji": "🌍",  "filter": "hue-rotate(120deg) saturate(1.5)"},
]

MBTI_LIST = [
    "INFJ", "INFP", "INTJ", "INTP",
    "ISFJ", "ISFP", "ISTJ", "ISTP",
    "ENFJ", "ENFP", "ENTJ", "ENTP",
    "ESFJ", "ESFP", "ESTJ", "ESTP"
]

css = """
<style>
    html, body, #root, .stApp,
    [data-testid="stAppViewContainer"], .main {
        background:
            radial-gradient(ellipse at 15% 30%, rgba(232,160,168,0.08) 0%, transparent 45%),
            radial-gradient(ellipse at 85% 70%, rgba(255,215,0,0.07) 0%, transparent 45%),
            url("data:image/png;base64,__CHUNSIK__"),
            radial-gradient(white 1px, transparent 1px) 0 0 / 70px 70px,
            radial-gradient(white 0.8px, transparent 0.8px) 35px 35px / 70px 70px,
            radial-gradient(rgba(255,255,255,0.4) 1px, transparent 1px) 18px 18px / 45px 45px,
            radial-gradient(rgba(255,215,0,0.3) 1px, transparent 1px) 50px 10px / 80px 80px,
            #0a0a0a !important;
        background-size: auto, auto, 33.33vw, 70px 70px, 70px 70px, 45px 45px, 80px 80px !important;
        background-repeat: no-repeat, no-repeat, repeat, repeat, repeat, repeat, repeat !important;
    }

    .block-container {
        background: rgba(18, 8, 18, 0.93) !important;
        border-radius: 28px;
        padding: 2rem 2rem 3rem 2rem;
        margin: 1.5rem 1rem 2rem 1rem !important;
        max-width: 95% !important;
        border: 1px solid rgba(255, 215, 0, 0.25);
        box-shadow: 0 8px 40px rgba(232, 160, 168, 0.15), 0 0 80px rgba(255, 215, 0, 0.05);
    }

    h1 {
        text-align: center;
        color: #FFD700 !important;
        white-space: nowrap !important;
        font-size: clamp(1.5rem, 6vw, 2.3rem) !important;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
    }
    h1 a, h2 a, h3 a { display: none !important; }

    h3 {
        font-size: clamp(0.9rem, 3.5vw, 1.05rem) !important;
        color: #ff85a1 !important;
        text-shadow: 0 0 12px rgba(255, 133, 161, 0.6);
    }

    p, label, .stSelectbox label, .stTextInput label {
        color: #d4c5d0 !important;
    }

    .stTextInput input, .stSelectbox select {
        background: rgba(255,255,255,0.92) !important;
        color: #1a0818 !important;
        border: 1px solid rgba(255, 215, 0, 0.5) !important;
        border-radius: 10px !important;
    }

    .stButton {
        display: flex !important;
        justify-content: center !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #c9a96e, #FFD700) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        padding: 0.6rem 1.5rem !important;
        width: auto !important;
        min-width: 60% !important;
        display: block !important;
        margin: 0 auto !important;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.4);
        text-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }
    .stButton > button * {
        color: white !important;
        background: transparent !important;
    }

    .card-back {
        background: linear-gradient(135deg, #1a0818, #2d1030);
        border: 2px solid rgba(255, 215, 0, 0.6);
        border-radius: 24px;
        padding: 1.8rem 1rem;
        text-align: center;
        margin: 1rem auto;
        max-width: 200px;
        box-shadow: 0 0 30px rgba(232, 160, 168, 0.25), 0 0 60px rgba(255,215,0,0.1), 0 8px 24px rgba(0,0,0,0.5);
    }

    .tarot-card {
        background: linear-gradient(135deg, #1a0818, #2d1030);
        border: 2px solid #FFD700;
        border-radius: 24px;
        padding: 1.5rem 1rem;
        text-align: center;
        margin: 1rem auto;
        font-size: 3rem;
        max-width: 200px;
        box-shadow: 0 0 40px rgba(255, 215, 0, 0.25), 0 8px 32px rgba(0,0,0,0.6);
    }

    .tarot-card-name {
        font-size: 1.4rem;
        font-weight: bold;
        color: #FFD700;
        text-align: center;
        margin: 0.5rem 0 1.2rem 0;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.4);
    }

    .result-box {
        background: rgba(25, 10, 25, 0.7);
        border-radius: 16px;
        padding: 1.5rem;
        border-left: 4px solid #e8a0a8;
        color: #f0e8f0;
        font-size: 1rem;
        line-height: 1.9;
    }

    .gallery-card {
        background: rgba(25, 10, 25, 0.8);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 16px;
        padding: 1rem;
        margin: 0.7rem 0;
        color: #f0e8f0;
        font-size: 0.9rem;
        line-height: 1.7;
    }
    .gallery-card-title {
        color: #FFD700;
        font-weight: bold;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }

    hr { border-color: rgba(255, 215, 0, 0.3) !important; }
    header[data-testid="stHeader"],
    [data-testid="stToolbar"] { display: none !important; }

    .chunsik-card-img {
        width: 80px;
        height: 80px;
        background: url("data:image/png;base64,__CHUNSIK__") center/contain no-repeat;
        display: block;
        margin: 0 auto;
    }
    .chunsik-card-back-img {
        width: 90px;
        height: 90px;
        background: url("data:image/png;base64,__CHUNSIK__") center/contain no-repeat;
        display: block;
        margin: 0 auto;
    }
</style>
"""
st.markdown(css.replace("__CHUNSIK__", chunsik_b64), unsafe_allow_html=True)

# 헤더
st.markdown("# 🐱 춘식이의 타로카페 🐱")
st.markdown(
    "<p style='text-align:center; color:#e8a0a8; font-size:1rem;'>"
    "오늘 하루를 타로카드로 점쳐드릴게요 🔮</p>",
    unsafe_allow_html=True
)
st.divider()

# 입력
st.subheader("🌙 누구의 운세를 볼까요?")
name = st.text_input("이름", placeholder="예: 아이린")
mbti = st.selectbox("MBTI", ["선택해주세요"] + MBTI_LIST)
st.divider()

# session_state 초기화
for key in ["card_drawn", "selected_card", "fortune_result"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "card_drawn" else None
if "gallery" not in st.session_state:
    st.session_state.gallery = []

# 카드 뽑기 전
if not st.session_state.card_drawn:
    st.markdown(
        "<div class='card-back'>"
        "<div style='font-size:0.6rem; color:#FFD700; letter-spacing:5px; margin-bottom:0.8rem;'>✦ ✦ ✦ ✦ ✦</div>"
        "<div class='chunsik-card-back-img'></div>"
        "<div style='font-size:0.55rem; color:#e8a0a8; margin-top:0.8rem; letter-spacing:2px;'>✨ 춘식이의 타로카페 ✨</div>"
        "<div style='font-size:0.6rem; color:#FFD700; letter-spacing:5px; margin-top:0.5rem;'>✦ ✦ ✦ ✦ ✦</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; color:#c9a96e; margin-top:0.5rem;'>"
        "카드가 당신을 기다리고 있어요...</p>",
        unsafe_allow_html=True
    )

    _, col, _ = st.columns([1, 2, 1])
    if col.button("🔮 타로카드 뽑기! 🔮", use_container_width=True):
        if not name or mbti == "선택해주세요":
            st.warning("이름과 MBTI를 먼저 입력해주세요 🙏")
        else:
            placeholder = st.empty()
            frames = ["🎴", "💫", "✨", "🌟", "🔮", "⭐", "💫", "✨", "🎴"]
            for frame in frames:
                placeholder.markdown(
                    "<div style='text-align:center; font-size:5rem; margin:1rem 0;'>"
                    + frame + "</div>",
                    unsafe_allow_html=True
                )
                time.sleep(0.13)
            placeholder.empty()

            card = random.choice(TAROT_CARDS)
            st.session_state.selected_card = card

            with st.spinner("춘식이가 카드를 읽는 중... 🐱"):
                prompt = (
                    "당신은 귀엽고 신비로운 타로카페 '춘식이의 타로카페'의 타로 리더입니다.\n"
                    "아래 정보를 바탕으로 오늘의 운세를 따뜻하고 공감 가는 한국어로 알려주세요.\n\n"
                    f"이름: {name}\n"
                    f"MBTI: {mbti}\n"
                    f"뽑힌 타로카드: {card['name']}\n\n"
                    "작성 규칙:\n"
                    "- 오직 한국어로만 작성! 영어, 로마자, 외국어 단어 절대 사용 금지!\n"
                    "- 카드 이름도 영어로 쓰지 말고 한국어로만!\n"
                    "- 귀엽고 따뜻한 말투로 (존댓말)\n"
                    f"- 오늘의 총운: 3~4문장으로 카드의 의미를 {name}님의 하루에 연결해서\n"
                    f"- {mbti} 성격 특성을 자연스럽게 반영\n"
                    "- 마지막에 '🌟 오늘의 한마디:' 로 짧고 인상적인 한 문장\n"
                    "- 이모지를 자연스럽게 활용\n"
                    "- 너무 무겁거나 부정적이지 않게, 희망적이고 따뜻하게!"
                )

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "당신은 오직 한국어만으로 대화하는 타로 리더입니다. 영어 단어, 로마자 알파벳, 일본어, 한자 등 외국어는 절대로 사용하면 안 됩니다. MBTI 약어(예: INFJ, ENFP)와 이모지만 예외로 허용됩니다. 만약 외국어가 포함되면 실패한 답변입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                st.session_state.fortune_result = response.choices[0].message.content

            st.session_state.card_drawn = True
            st.rerun()

# 결과 표시
if st.session_state.card_drawn and st.session_state.selected_card:
    card = st.session_state.selected_card

    # 카드마다 다른 색상의 춘식이!
    st.markdown(
        "<div class='tarot-card'>"
        "<div style='font-size:0.55rem; color:#FFD700; letter-spacing:4px; margin-bottom:0.6rem;'>✦ ✦ ✦ ✦ ✦</div>"
        f"<div class='chunsik-card-img' style='filter:{card['filter']};'></div>"
        f"<div style='font-size:2rem; margin-top:0.3rem;'>{card['emoji']}</div>"
        "<div style='font-size:0.55rem; color:#FFD700; letter-spacing:4px; margin-top:0.6rem;'>✦ ✦ ✦ ✦ ✦</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='tarot-card-name'>✨ " + card["name"] + " ✨</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='result-box'>" + st.session_state.fortune_result + "</div>",
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2 = st.columns(2)
    # 갤러리 저장 버튼
    if col1.button("📸 갤러리에 저장!", use_container_width=True):
        st.session_state.gallery.append({
            "name": name,
            "mbti": mbti,
            "card": card["name"],
            "emoji": card["emoji"],
            "result": st.session_state.fortune_result
        })
        st.success("갤러리에 저장됐어요! 🌟")

    # 다시 뽑기 버튼
    if col2.button("🔄 다시 뽑기", use_container_width=True):
        st.session_state.card_drawn = False
        st.session_state.selected_card = None
        st.session_state.fortune_result = None
        st.rerun()

# 갤러리 섹션
if st.session_state.gallery:
    st.divider()
    st.subheader("✨ 오늘의 운세 갤러리")
    for i, item in enumerate(reversed(st.session_state.gallery)):
        st.markdown(
            f"<div class='gallery-card'>"
            f"<div class='gallery-card-title'>{item['emoji']} {item['name']} ({item['mbti']}) · {item['card']} 카드</div>"
            f"{item['result']}"
            f"</div>",
            unsafe_allow_html=True
        )
