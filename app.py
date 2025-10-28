import streamlit as st
import random
import math
import numpy as np
import matplotlib.pyplot as plt

# 원본 'blob' 함수 (변경 없음)
def blob(center=(0.5, 0.5), r=0.3, points=50, wobble=0.15):
    # generate a wobbly closed shape
    angles = np.linspace(0, 2*math.pi, points)
    radii = r * (1 + wobble*(np.random.rand(points)-0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y

# 포스터를 생성하는 함수
def generate_poster(n_layers):
    random.seed() # 실행 시마다 새로운 랜덤 시드
    
    # Matplotlib Figure 객체 생성
    fig, ax = plt.subplots(figsize=(7, 10))
    ax.axis('off')

    # background
    ax.set_facecolor((0.98, 0.98, 0.97))

    # --- 수동 팔레트 정의 ---
    palette = [
        (0.1, 0.3, 0.6),   # 진한 파랑
        (0.5, 0.7, 0.9),   # 중간 파랑
        (0.8, 0.9, 1.0),   # 연한 파랑
        (1.0, 0.5, 0.2),   # 주황색 (포인트 컬러)
        (0.3, 0.3, 0.3)    # 어두운 회색
    ]

    for i in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.1, 0.4) 

        # 'blob'의 points 값을 50으로 고정 (함수 정의에서 변경)
        x, y = blob(center=(cx, cy), r=rr, wobble=random.uniform(0.1, 0.4))

        color = random.choice(palette)
        alpha = random.uniform(0.6, 0.9)

        # ax.fill을 사용 (plt.fill 대신)
        ax.fill(x, y,
                 color=color,
                 alpha=alpha,
                 edgecolor='black', # 검은색 외곽선
                 linewidth=0.5)     # 얇은 선

    # --- 텍스트 레이블 수정 (ax.text 사용) ---
    ax.text(0.05, 0.95, "Generative Poster [Variation]", fontsize=18, weight='bold', transform=ax.transAxes)
    ax.text(0.05, 0.91, "Practice • Changing Parameters", fontsize=11, transform=ax.transAxes)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # plt.show() 대신 figure 객체를 반환
    return fig

# --- Streamlit 앱 인터페이스 ---

st.set_page_config(layout="centered")
st.title("Generative Poster 🎨")

# 레이어 수를 조절하는 슬라이더
n_layers = st.slider("Number of Layers", min_value=5, max_value=30, value=10, step=1)

# 포스터 생성
poster_fig = generate_poster(n_layers)

# Streamlit에 포스터 표시
st.pyplot(poster_fig, use_container_width=True)

st.caption("A generative art poster deployed with Streamlit Cloud.")