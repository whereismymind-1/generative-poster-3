import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D, Poly3DCollection
from matplotlib.animation import FuncAnimation
import simplex_noise  # Perlin Noise를 위한 라이브러리
import os

# --- 1. 원본 코드에 누락된 필수 설정 정의 ---

# 3D 배경 그리드 생성
grid_res = 50
x_lin = np.linspace(-4, 4, grid_res)
y_lin = np.linspace(-4, 4, grid_res)
X_grid, Y_grid = np.meshgrid(x_lin, y_lin)

# 3D 회전 행렬 함수
def get_rotation_matrix(angle_rad, axis='z'):
    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
    if axis == 'z':
        return np.array([
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ])
    # (다른 축도 추가 가능)

# 3D 큐브 객체 생성 함수
def create_cube():
    v = 1.0  # 정육면체 한 변 길이의 절반
    vertices = [
        np.array([-v, -v, -v]), np.array([v, -v, -v]), np.array([v, v, -v]), np.array([-v, v, -v]),
        np.array([-v, -v, v]), np.array([v, -v, v]), np.array([v, v, v]), np.array([-v, v, v])
    ]
    # 6개의 면 정의
    faces_idx = [
        [vertices[0], vertices[1], vertices[2], vertices[3]], # bottom
        [vertices[4], vertices[5], vertices[6], vertices[7]], # top
        [vertices[0], vertices[1], vertices[5], vertices[4]], # front
        [vertices[2], vertices[3], vertices[7], vertices[6]], # back
        [vertices[1], vertices[2], vertices[6], vertices[5]], # right
        [vertices[0], vertices[3], vertices[7], vertices[4]]  # left
    ]
    return faces_idx

# 장면에 배치할 객체 목록 (큐브 1개)
scene_objects = [
    {
        'faces': create_cube(),
        'pos': np.array([0, 0, 0]),  # 위치
        'rot_speed': 1.5,
        'color': (0.9, 0.1, 0.5, 0.7), # Y2K 핑크/마젠타
        'alpha': 0.8
    }
]

# 텍스트 회전 속도
text_rot_speed = -1.0
gif_filename = 'animated_poster.gif'

# --- 2. 애니메이션 로직을 클래스로 캡슐화 ---
# FuncAnimation이 Streamlit 리로드 시 꼬이지 않게 하기 위함

class Y2KAnimator:
    def __init__(self, fig, ax, x_grid, y_grid, scene_objects, text_rot_speed):
        self.fig = fig
        self.ax = ax
        self.X_grid = x_grid
        self.Y_grid = y_grid
        self.scene_objects = scene_objects
        self.text_rot_speed = text_rot_speed

    # 이 함수가 원본 코드의 'update' 함수입니다.
    def update(self, frame):
        self.ax.clear()
        self.ax.set_axis_off() # 축 숨기기

        # 배경 왜곡 (Perlin Noise)
        Z_grid = np.zeros_like(self.X_grid)
        for i in range(self.X_grid.shape[0]):
            for j in range(self.Y_grid.shape[1]):
                Z_grid[i, j] = simplex_noise.noise3(x=self.X_grid[i, j] * 0.3, y=self.Y_grid[i, j] * 0.3, z=frame * 0.05) * 2

        # 배경 표면 그리기
        self.ax.plot_surface(self.X_grid, self.Y_grid, Z_grid, cmap='viridis', rstride=1, cstride=1, alpha=0.6, linewidth=0)

        # 3D 뷰 설정
        self.ax.set_xlim([-4, 4]); self.ax.set_ylim([-4, 4]); self.ax.set_zlim([-5, 5])
        self.ax.dist = 8
        self.ax.view_init(elev=20, azim=frame * 0.5)

        # 모든 객체를 개별적으로 회전하고 그리기
        for obj in self.scene_objects:
            angle_rad = np.radians(frame * obj['rot_speed'])
            rot_matrix = get_rotation_matrix(angle_rad)
            rotated_faces = []
            for face in obj['faces']:
                rotated_face = [np.dot(rot_matrix, vertex) + obj['pos'] for vertex in face]
                rotated_faces.append(rotated_face)
            self.ax.add_collection3d(Poly3DCollection(
                rotated_faces,
                facecolors=obj['color'],
                linewidths=1.5,
                edgecolors='white',
                alpha=obj['alpha']
            ))

        # 3D "lost" 텍스트 그리기
        self.ax.text(
            0, 0, 0.5, "lost",
            color='lime', fontsize=24, fontweight='bold',
            fontfamily='monospace', ha='center', va='center',
            rotation=frame * self.text_rot_speed
        )

# --- 3. Streamlit 앱 인터페이스 ---

st.set_page_config(layout="centered", page_title="Y2K GIF Generator")
st.title("Y2K Animated Poster 👾")
st.write("버튼을 클릭하여 3D Y2K 스타일 애니메이션 GIF를 생성합니다. (약 1-2분 소요)")

# GIF 파라미터 조절 (사이드바)
st.sidebar.header("GIF Settings")
total_frames = st.sidebar.slider("Total Frames (GIF 길이)", 10, 200, 75, 5)
gif_fps = st.sidebar.slider("FPS (초당 프레임)", 10, 30, 20, 1)
st.sidebar.info(f"예상 GIF 길이: {total_frames / gif_fps:.1f} 초")

# GIF 생성 버튼
if st.button("🚀 Generate GIF"):
    
    with st.spinner(f"애니메이션 생성 중... (총 {total_frames} 프레임)"):
        # 1. 매번 새로운 Figure 객체 생성 (중요)
        plt.close('all') # 이전 플롯 닫기
        fig = plt.figure(figsize=(7, 7)) # 웹에 적합하게 크기 살짝 줄임
        ax = fig.add_subplot(111, projection='3d')

        # 2. 애니메이터 객체 생성
        animator = Y2KAnimator(fig, ax, X_grid, Y_grid, scene_objects, text_rot_speed)

        # 3. FuncAnimation 객체 생성
        anim = FuncAnimation(fig, animator.update, frames=total_frames, interval=50)

        # 4. GIF 저장 (진행률 표시)
        progress_bar = st.progress(0.0)
        
        # anim.save의 콜백 함수를 사용해 streamlit 프로그레스 바 업데이트
        def progress_callback(current_frame, total_frames):
            progress_bar.progress(float(current_frame + 1) / float(total_frames))

        # pillow 라이터를 사용해 GIF 저장
        anim.save(gif_filename, writer='pillow', fps=gif_fps, progress_callback=progress_callback)
        
        plt.close(fig) # 리소스 정리
        progress_bar.empty() # 프로그레스 바 숨기기

    st.success(f"'{gif_filename}' 생성 완료!")

    # 5. 생성된 GIF 표시 및 다운로드 버튼 제공
    st.image(gif_filename)
    
    with open(gif_filename, "rb") as file:
        st.download_button(
            label="Download GIF",
            data=file,
            file_name="y2k_poster.gif",
            mime="image/gif"
        )
else:
    st.info("설정을 조절하고 'Generate GIF' 버튼을 누르세요.")