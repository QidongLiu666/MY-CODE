import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io
from PIL import Image

# ====================== 终极绝杀：强制加载中文字体，本地/云端都有字 ======================
plt.rcParams['axes.unicode_minus'] = False

import matplotlib.font_manager as fm

# 直接加载 WenQuanYi Zen Hei（Streamlit 自带，100% 存在）
try:
    font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
except:
    # 备用方案
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'SimHei', 'DejaVu Sans']

# ====================== 核心计算逻辑（完全不变） ======================
def 分配标本_新手合并(总数, 总医生数, 新手编号列表):
    新手数 = len(新手编号列表)
    普通医生数 = 总医生数 - 新手数
    等效医生数 = 普通医生数 + (新手数 + 1) // 2

    每份 = 总数 // 等效医生数
    余数 = 总数 % 等效医生数

    结果 = [每份 if (i+1 not in 新手编号列表) else 0 for i in range(总医生数)]
    
    for i in range(总医生数):
        if 余数 <= 0:
            break
        if (i+1 not in 新手编号列表):
            结果[i] += 1
            余数 -= 1

    新手组 = [新手编号列表[i:i+2] for i in range(0, len(新手编号列表), 2)]
    for 组 in 新手组:
        if len(组) == 2:
            组总量 = 每份
            if 余数 > 0:
                组总量 += 1
                余数 -= 1
            半1 = 组总量 // 2
            半2 = 组总量 - 半1
            结果[组[0]-1] = 半1
            结果[组[1]-1] = 半2
        else:
            结果[组[0]-1] = 每份 // 2
    return 结果

def 分配标本_普通(总数, 人数):
    每份 = 总数 // 人数
    余数 = 总数 % 人数
    结果 = []
    for i in range(人数):
        本次 = 每份 + (1 if i < 余数 else 0)
        结果.append(本次)
    return 结果

def 级联分配(初诊列表, 复诊人数):
    总标本 = sum(初诊列表)
    复诊分配 = 分配标本_普通(总标本, 复诊人数)
    
    复诊接收 = [[] for _ in range(复诊人数)]
    复诊索引 = 0
    当前余量 = 复诊分配[复诊索引]
    
    for 医生i, 数量 in enumerate(初诊列表):
        剩余 = 数量
        while 剩余 > 0:
            给 = min(剩余, 当前余量)
            复诊接收[复诊索引].append((医生i+1, 给))
            剩余 -= 给
            当前余量 -= 给
            if 当前余量 == 0:
                复诊索引 += 1
                if 复诊索引 < 复诊人数:
                    当前余量 = 复诊分配[复诊索引]
    return 复诊分配, 复诊接收

# ====================== 画图函数 ======================
def 画分配图(初诊姓名, 复诊姓名, 复诊总量, 初诊分配, 复诊明细, 标题, ax):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    ax.set_title(标题, fontsize=26, pad=30, fontweight='bold')

    初诊_x = 2
    初诊_y_step = 1.5
    初诊_y_start = 10.5
    初诊_pos = {}
    for i, name in enumerate(初诊姓名):
        y = 初诊_y_start - i * 初诊_y_step
        初诊_pos[i+1] = (初诊_x, y)
        ax.text(初诊_x, y, f"{name}：{初诊分配[i]}例", ha='right', va='center',
                fontsize=18, fontweight='bold')

    复诊_x = 7
    复诊_y_step = 1.5
    复诊_y_start = 10.5
    复诊_pos = {}
    圈数字 = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
    for i, (name, total) in enumerate(zip(复诊姓名, 复诊总量)):
        y = 复诊_y_start - i * 初诊_y_step
        复诊_pos[i] = (复诊_x, y)
        ax.text(复诊_x, y, f"{total}例 {圈数字[i]} {name}", ha='left', va='center',
                fontsize=18, fontweight='bold')

    for 复诊_idx, 明细_list in enumerate(复诊明细):
        rx, ry = 复诊_pos[复诊_idx]
        for (初诊号, 数量) in 明细_list:
            ix, iy = 初诊_pos[初诊号]
            ax.plot([ix + 0.15, rx - 0.15], [iy, ry], color='black', linewidth=1.2)
            mid_x = (ix + rx) / 2
            mid_y = (iy + ry) / 2
            ax.text(mid_x, mid_y, f"{数量}", ha='center', va='center', 
                    fontsize=16, color='red', fontweight='bold')

def 显示合并图(初诊姓名, 小复诊姓名, 小复诊总量, 小初诊, 小复诊明细, 大复诊姓名, 大复诊总量, 大初诊, 大复诊明细, 小标本, 大标本):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10), gridspec_kw={'wspace': 0.1})
    
    画分配图(初诊姓名, 小复诊姓名, 小复诊总量, 小初诊, 小复诊明细, f"小标本：{小标本}例", ax1)
    画分配图(初诊姓名, 大复诊姓名, 大复诊总量, 大初诊, 大复诊明细, f"大标本：{大标本}例", ax2)
    
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    
    canvas = FigureCanvasAgg(fig)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    img = Image.open(buf)
    plt.close(fig)
    return img

# ====================== 网页界面 ======================
st.set_page_config(page_title="病理标本分配计算器", layout="wide")
st.title("🧪 病理标本分配系统（网页版）")

st.subheader("📝 输入信息")
col1, col2 = st.columns(2)
with col1:
    大标本 = st.number_input("大标本数量", min_value=0, value=48, step=1)
    初诊人数 = st.number_input("初诊医生总数", min_value=1, value=5, step=1)
    小复诊人数 = st.number_input("小标本复诊人数", min_value=1, value=3, step=1)
with col2:
    小标本 = st.number_input("小标本数量", min_value=0, value=125, step=1)
    新手编号 = st.text_input("新手医生编号（用英文逗号分隔，如 5,6）", value="")
    大复诊人数 = st.number_input("大标本复诊人数", min_value=1, value=3, step=1)

st.subheader("👨‍⚕️ 复诊老师姓名")
col3, col4 = st.columns(2)
with col3:
    st.markdown("**小标本复诊老师**")
    小复诊姓名 = []
    for i in range(小复诊人数):
        姓名 = st.text_input(f"小复诊老师 {i+1}", value=f"老师{i+1}", key=f"小复诊{i}")
        小复诊姓名.append(姓名)
with col4:
    st.markdown("**大标本复诊老师**")
    大复诊姓名 = []
    for i in range(大复诊人数):
        姓名 = st.text_input(f"大复诊老师 {i+1}", value=f"老师{i+1}", key=f"大复诊{i}")
        大复诊姓名.append(姓名)

try:
    新手编号列表 = [int(x.strip()) for x in 新手编号.split(",") if x.strip().isdigit()]
except:
    新手编号列表 = []
    st.warning("⚠️ 新手编号格式错误，请输入数字并用英文逗号分隔（如 5,6）")

if st.button("✅ 生成分配结构图", type="primary"):
    初诊姓名 = [f"初诊{i+1}" for i in range(初诊人数)]

    小初诊 = 分配标本_新手合并(小标本, 初诊人数, 新手编号列表)
    小复诊总量, 小复诊明细 = 级联分配(小初诊, 小复诊人数)

    大初诊 = 分配标本_新手合并(大标本, 初诊人数, 新手编号列表)
    大复诊总量, 大复诊明细 = 级联分配(大初诊, 大复诊人数)

    st.markdown("---")
    if 小标本 > 0 or 大标本 > 0:
        合并图 = 显示合并图(初诊姓名, 小复诊姓名, 小复诊总量, 小初诊, 小复诊明细, 
                           大复诊姓名, 大复诊总量, 大初诊, 大复诊明细, 小标本, 大标本)
        st.image(合并图, use_column_width=True)
        st.success("✅ 分配结构图已生成！")
    else:
        st.info("请输入大标本或小标本数量以生成结构图。")
