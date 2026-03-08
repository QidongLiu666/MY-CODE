import streamlit as st

# ====================== 核心计算逻辑（未改动） ======================
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
    结果 = [每份 + (1 if i < 余数 else 0) for i in range(人数)]
    return 结果

def 级联分配(初诊列表, 复诊人数):
    总标本 = sum(初诊列表)
    复诊分配 = 分配标本_普通(总标本, 复诊人数)
    
    复诊接收 = [[] for _ in range(复诊人数)]
    复诊_idx = 0
    当前余量 = 复诊分配[复诊_idx]
    
    for 医生i, 数量 in enumerate(初诊列表):
        剩余 = 数量
        while 剩余 > 0:
            给 = min(剩余, 当前余量)
            复诊接收[复诊_idx].append((医生i+1, 给))
            剩余 -= 给
            当前余量 -= 给
            if 当前余量 == 0:
                复诊_idx += 1
                if 复诊_idx < 复诊人数:
                    当前余量 = 复诊分配[复诊_idx]
    return 复诊分配, 复诊接收

# ====================== 画图函数（关键修改：仅保留带圈数字+例数，删除初诊文字） ======================
def 画分配图_干净版(初诊姓名, 复诊姓名, 复诊总量, 初诊分配, 复诊明细, 标题):
    圈数字 = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
    n_chuzhen = len(初诊姓名)
    n_fuzhen = len(复诊姓名)
    
    line_height = 45
    start_y = 60
    left_x = 80
    right_x = 215  # 线段长度=135，原长3/4
    svg_height = start_y + max(n_chuzhen, n_fuzhen) * line_height + 30
    
    html = f"""
    <div style="width:100%; margin:5px auto;">
        <h3 style="text-align:center; font-size:17px; margin:0; padding:0;">{标题}</h3>
        <svg width="100%" height="{svg_height}" style="font-family: sans-serif;">
    """
    
    # 初诊：仅带圈数字 + 例数（如 ① 25例），无任何多余文字
    for i in range(n_chuzhen):
        y = start_y + i * line_height
        html += f'<text x="{left_x - 15}" y="{y}" text-anchor="end" font-size="14px">{圈数字[i]} {初诊分配[i]}例</text>'
    
    # 复诊：保留原有样式，标签带“标本”
    for i in range(n_fuzhen):
        y = start_y + i * line_height
        html += f'<text x="{right_x + 10}" y="{y}" font-size="14px">{复诊总量[i]}例 {圈数字[i]} {复诊姓名[i]}</text>'
    
    # 连线（长度固定，手机适配）
    for 复诊_idx, 明细_list in enumerate(复诊明细):
        for (初诊号, 数量) in 明细_list:
            y1 = start_y + (初诊号 - 1) * line_height
            y2 = start_y + 复诊_idx * line_height
            mid_x = (left_x + right_x) / 2
            mid_y = (y1 + y2) / 2
            html += f'<line x1="{left_x}" y1="{y1}" x2="{right_x}" y2="{y2}" stroke="#666" stroke-width="1"/>'
            html += f'<text x="{mid_x}" y="{mid_y - 3}" font-size="13px" font-weight="bold" fill="red" text-anchor="middle">{数量}</text>'
    
    html += """
        </svg>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ====================== 网页界面（未改动，标签带“标本”） ======================
st.set_page_config(page_title="病理标本分配", layout="wide")
st.title("🧪 病理标本分配系统")

st.subheader("📝 输入信息")
col1, col2 = st.columns(2)
with col1:
    大标本数量 = st.number_input("大标本数量", min_value=0, value=48, step=1)
    初诊医生总数 = st.number_input("初诊医生总数", min_value=1, value=5, step=1)
    小标本复诊人数 = st.number_input("小标本复诊人数", min_value=1, value=3, step=1)
with col2:
    小标本数量 = st.number_input("小标本数量", min_value=0, value=125, step=1)
    新手编号 = st.text_input("新手医生编号（英文逗号分隔）", value="")
    大标本复诊人数 = st.number_input("大标本复诊人数", min_value=1, value=3, step=1)

st.subheader("👨‍⚕️ 复诊老师姓名")
col3, col4 = st.columns(2)
with col3:
    st.markdown("**小标本复诊老师**")
    小复诊姓名 = [st.text_input(f"小标本复诊老师 {i+1}", value=f"老师{i+1}", key=f"小{i}") for i in range(小标本复诊人数)]
with col4:
    st.markdown("**大标本复诊老师**")
    大复诊姓名 = [st.text_input(f"大标本复诊老师 {i+1}", value=f"老师{i+1}", key=f"大{i}") for i in range(大标本复诊人数)]

try:
    新手编号列表 = [int(x.strip()) for x in 新手编号.split(",") if x.strip().isdigit()]
except:
    新手编号列表 = []

if st.button("✅ 生成分配结构图", type="primary"):
    初诊姓名 = [f"初诊{i+1}" for i in range(初诊医生总数)]  # 仅用于计数，前端不显示
    
    小初诊 = 分配标本_新手合并(小标本数量, 初诊医生总数, 新手编号列表)
    小复诊总量, 小复诊明细 = 级联分配(小初诊, 小标本复诊人数)

    大初诊 = 分配标本_新手合并(大标本数量, 初诊医生总数, 新手编号列表)
    大复诊总量, 大复诊明细 = 级联分配(大初诊, 大标本复诊人数)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        画分配图_干净版(初诊姓名, 小复诊姓名, 小复诊总量, 小初诊, 小复诊明细, f"小标本：{小标本数量}例")
    with c2:
        画分配图_干净版(初诊姓名, 大复诊姓名, 大复诊总量, 大初诊, 大复诊明细, f"大标本：{大标本数量}例")
