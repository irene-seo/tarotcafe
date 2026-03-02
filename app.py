import streamlit as st
import os
import base64
import random
import time
import re
import io
from PIL import Image, ImageDraw, ImageFont
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

MBTI_PATTERN = r'\b(INFJ|INFP|INTJ|INTP|ISFJ|ISFP|ISTJ|ISTP|ENFJ|ENFP|ENTJ|ENTP|ESFJ|ESFP|ESTJ|ESTP)\b'

def has_foreign_text(text):
    """MBTI 약어 제외하고 외국어(알파벳 2글자 이상, 한자, 일본어) 있으면 True"""
    cleaned = re.sub(MBTI_PATTERN, '', text)
    if re.search(r'[a-zA-Z]{2,}', cleaned):
        return True
    # 한자(CJK), 일본어 히라가나/가타카나 감지
    if re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', cleaned):
        return True
    return False

def get_font(size):
    """한글 지원 폰트 찾기"""
    paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "C:/Windows/Fonts/malgun.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            pass
    return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    """한글 텍스트 줄 나누기"""
    lines = []
    for paragraph in text.split('\n'):
        if not paragraph.strip():
            lines.append('')
            continue
        line = ''
        for char in paragraph:
            test = line + char
            try:
                w = draw.textlength(test, font=font)
            except:
                w = len(test) * 17
            if w > max_width and line:
                lines.append(line)
                line = char
            else:
                line = test
        if line:
            lines.append(line)
    return lines

def make_result_image(card_name, fortune_text, name, mbti):
    W, H = 540, 960
    img = Image.new('RGB', (W, H), (10, 8, 18))
    draw = ImageDraw.Draw(img)

    GOLD = (255, 215, 0)
    PINK = (232, 160, 168)
    WHITE = (240, 232, 240)

    f_header = get_font(22)
    f_card   = get_font(26)
    f_body   = get_font(17)
    f_small  = get_font(15)

    # 테두리
    draw.rectangle([12, 12, W-12, H-12], outline=GOLD, width=2)

    # 헤더
    draw.text((W//2, 45), "춘식이의 타로카페", font=f_header, fill=GOLD, anchor="mm")
    draw.line([(30, 68), (W-30, 68)], fill=GOLD, width=1)

    # 카드 이름
    draw.text((W//2, 105), f"[ {card_name} ]", font=f_card, fill=GOLD, anchor="mm")
    draw.line([(30, 130), (W-30, 130)], fill=(100, 80, 100), width=1)

    # 운세 텍스트
    lines = wrap_text(draw, fortune_text, f_body, W - 80)
    y = 150
    for line in lines:
        if line:
            draw.text((40, y), line, font=f_body, fill=WHITE)
            y += 28
        else:
            y += 12

    # 하단
    draw.line([(30, H-60), (W-30, H-60)], fill=GOLD, width=1)
    draw.text((W//2, H-35), f"{name}  ·  {mbti}", font=f_small, fill=PINK, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()

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

            random.seed()
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

                system_msg = (
                    "당신은 오직 한국어만으로 대화하는 타로 리더입니다. "
                    "영어, 독일어, 프랑스어, 일본어, 중국어, 한자(漢字), 스페인어, 이탈리아어 등 "
                    "모든 외국어 단어와 문자는 절대 사용하면 안 됩니다. "
                    "한자(예: 愛, 運, 幸 등)도 절대 사용 금지입니다. "
                    "한국어 이름이나 단어를 로마자로 표기하는 것도 절대 금지입니다. "
                    "예를 들어 'chun식', 'Chunsik', 'tarot' 같은 혼용은 절대 안 됩니다. "
                    "MBTI 약어(예: INFJ, ENFP)와 이모지만 예외로 허용됩니다. "
                    "반드시 순수한 한국어 단어로만 작성하세요."
                )
                fortune_result = None
                for _ in range(5):
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=500,
                        temperature=0.6
                    )
                    result = response.choices[0].message.content
                    if not has_foreign_text(result):
                        fortune_result = result
                        break
                st.session_state.fortune_result = fortune_result or result

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

    img_bytes = make_result_image(card["name"], st.session_state.fortune_result, name, mbti)
    col1, col2 = st.columns(2)
    col1.download_button(
        label="📱 이미지로 저장!",
        data=img_bytes,
        file_name=f"타로_{card['name']}_{name}.png",
        mime="image/png",
        use_container_width=True
    )
    if col2.button("🔄 다시 뽑기", use_container_width=True):
        st.session_state.card_drawn = False
        st.session_state.selected_card = None
        st.session_state.fortune_result = None
        st.rerun()
