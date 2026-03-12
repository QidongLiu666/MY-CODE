import streamlit as st

# ====================== 核心计算逻辑（完全不动） ======================
def 分配标本_新手合并(总数, 初诊医生编号列表, 新手编号集合):
    当量 = 0.0
    for 号 in 初诊医生编号列表:
        if 号 in 新手编号集合:
            当量 += 0.5
        else:
            当量 += 1.0

    每份当量 = 总数 / 当量 if 当量 != 0 else 0
    结果 = []
    总分配 = 0
    for 号 in 初诊医生编号列表:
        if 号 in 新手编号集合:
            数量 = int(每份当量 * 0.5)
        else:
            数量 = int(每份当量 * 1.0)
        结果.append(数量)
        总分配 += 数量

    余数 = 总数 - 总分配
    # 先给新手医生补余数（优先级更高）
    for i in range(len(初诊医生编号列表)):
        if 余数 <= 0:
            break
        if 初诊医生编号列表[i] in 新手编号集合:
            结果[i] += 1
            余数 -= 1
    # 再给普通医生补余数
    for i in range(len(初诊医生编号列表)):
        if 余数 <= 0:
            break
        if 初诊医生编号列表[i] not in 新手编号集合:
            结果[i] += 1
            余数 -= 1
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

# ====================== 新增：平衡非新手医生的标本总数 ======================
def 平衡非新手(小列表, 大列表, 是否新手列表):
    """
    调整非新手医生的标本数，使他们的总和尽可能相等（最大差≤1）
    只修改小列表和大列表，返回修改后的列表
    """
    while True:
        n = len(小列表)
        非新手索引 = [i for i in range(n) if not 是否新手列表[i]]
        if not 非新手索引:
            break
        当前总数 = [小列表[i] + 大列表[i] for i in 非新手索引]
        最大 = max(当前总数)
        最小 = min(当前总数)
        if 最大 - 最小 <= 1:
            break
        # 找到对应的原始索引
        最大索引 = 非新手索引[当前总数.index(最大)]
        最小索引 = 非新手索引[当前总数.index(最小)]
        # 尝试转移一份小标本，否则转移大标本
        if 小列表[最大索引] > 0:
            小列表[最大索引] -= 1
            小列表[最小索引] += 1
        elif 大列表[最大索引] > 0:
            大列表[最大索引] -= 1
            大列表[最小索引] += 1
        else:
            # 理论上不会发生，但以防死循环
            break
    return 小列表, 大列表

# ====================== 画图函数（完全不动） ======================
def 画分配图_干净版(初诊医生编号列表, 复诊姓名, 复诊总量, 初诊分配, 复诊明细, 标题):
    圈数字 = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
    n_chuzhen = len(初诊医生编号列表)
    n_fuzhen = len(复诊姓名)
    
    line_height = 45
    start_y = 30
    left_x = 80
    right_x = 215
    svg_height = start_y + max(n_chuzhen, n_fuzhen) * line_height + 10

    中文字体 = '"Microsoft YaHei", "PingFang SC", "Helvetica Neue", sans-serif'
    html = f"""
    <div style="width:100%; margin:2px auto;">
        <h3 style="text-align:center; font-size:17px; margin:0; padding:0; font-family:{中文字体};">{标题}</h3>
        <svg width="100%" height="{svg_height}" style="font-family:{中文字体};">
    """

    for i in range(n_chuzhen):
        y = start_y + i * line_height
        号 = 初诊医生编号列表[i]
        圈 = 圈数字[号 - 1] if 1 <= 号 <= 10 else str(号)
        html += f'<text x="{left_x - 15}" y="{y}" text-anchor="end" font-size="14px">{圈} {初诊分配[i]}例</text>'

    for i in range(n_fuzhen):
        y = start_y + i * line_height
        html += f'<text x="{right_x + 10}" y="{y}" font-size="14px">{复诊总量[i]}例 {圈数字[i]} {复诊姓名[i]}</text>'

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

# ====================== 网页界面（核心修复：生成严格重复的编号） ======================
st.set_page_config(page_title="病理标本分配", layout="wide")
st.title("🧪 病理标本分配系统")

st.subheader("📝 输入信息")
col1, col2 = st.columns(2)
with col1:
    大标本数量 = st.number_input("大标本数量", min_value=0, value=48, step=1)
    初诊医生总数 = st.number_input("初诊医生总数", min_value=1, value=7, step=1)
    小标本复诊人数 = st.number_input("小标本复诊人数", min_value=1, value=3, step=1)
with col2:
    小标本数量 = st.number_input("小标本数量", min_value=0, value=125, step=1)
    新手编号 = st.text_input("新手医生编号（英文逗号分隔，重复代表多个同号新手，如 4,4）", value="4,4")
    大标本复诊人数 = st.number_input("大标本复诊人数", min_value=1, value=3, step=1)

st.subheader("👨‍⚕️ 复诊老师姓名")
col3, col4 = st.columns(2)
with col3:
    st.markdown("**小标本复诊老师**")
    小复诊姓名 = [st.text_input(f"小标本复诊老师 {i+1}", value=f"老师{i+1}", key=f"小{i}") for i in range(小标本复诊人数)]
with col4:
    st.markdown("**大标本复诊老师**")
    大复诊姓名 = [st.text_input(f"大标本复诊老师 {i+1}", value=f"老师{i+1}", key=f"大{i}") for i in range(大标本复诊人数)]

# 解析新手编号
try:
    新手编号列表 = [int(x.strip()) for x in 新手编号.split(",") if x.strip().isdigit()]
except:
    新手编号列表 = []
    st.warning("⚠️ 新手编号格式错误，请输入数字并用英文逗号分隔（如 4,4）")

# 核心修复逻辑：生成初诊编号列表
# 逻辑：从1开始顺排，遇到新手编号，就连续插入对应次数
基础初诊编号 = []
当前号 = 1
新手计数器 = {}
for num in 新手编号列表:
    新手计数器[num] = 新手计数器.get(num, 0) + 1

while len(基础初诊编号) < 初诊医生总数:
    # 如果当前号是新手，且还有剩余次数，就继续追加同一个号
    if 新手计数器.get(当前号, 0) > 0:
        while 新手计数器.get(当前号, 0) > 0 and len(基础初诊编号) < 初诊医生总数:
            基础初诊编号.append(当前号)
            新手计数器[当前号] -= 1
        当前号 += 1
    else:
        基础初诊编号.append(当前号)
        当前号 += 1

# 确保长度准确（防溢出）
基础初诊编号 = 基础初诊编号[:初诊医生总数]

新手编号集合 = set(新手编号列表)

if st.button("✅ 生成分配结构图", type="primary"):

    # ====================== 小标本分配 ======================
    小初诊 = 分配标本_新手合并(小标本数量, 基础初诊编号, 新手编号集合)

    # ====================== 大标本分配（半份逻辑正确） ======================
    大初诊 = 分配标本_新手合并(大标本数量, 基础初诊编号, 新手编号集合)

    # ====================== 新增：平衡非新手医生的标本总数 ======================
    是否新手 = [编号 in 新手编号集合 for 编号 in 基础初诊编号]
    小初诊, 大初诊 = 平衡非新手(小初诊, 大初诊, 是否新手)

    # ====================== 重新计算复诊分配 ======================
    小复诊总量, 小复诊明细 = 级联分配(小初诊, 小标本复诊人数)
    大复诊总量, 大复诊明细 = 级联分配(大初诊, 大标本复诊人数)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        画分配图_干净版(基础初诊编号, 小复诊姓名, 小复诊总量, 小初诊, 小复诊明细, f"小标本：{小标本数量}例")
    with c2:
        画分配图_干净版(基础初诊编号, 大复诊姓名, 大复诊总量, 大初诊, 大复诊明细, f"大标本：{大标本数量}例")
