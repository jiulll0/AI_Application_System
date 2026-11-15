import streamlit as st
import pandas as pd
import plotly.express as px
import os
import warnings
import time

warnings.filterwarnings('ignore')

# ================= 1. 页面设置与高级 CSS =================
st.set_page_config(page_title="AI应用场景智能挖掘系统", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 32px !important; font-weight: 800; color: #4CAF50; text-align: center;}
    .sub-title { font-size: 16px; color: #888; text-align: center; margin-bottom: 20px;}
    .perm-box { padding: 15px; border-radius: 8px; background-color: #1e1e1e; border-left: 4px solid #FFC107;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 AI应用场景的智能挖掘与机会评估系统</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">端到端分析系统：需求驱动 -> 数据采集 -> 智能判别 -> 价值评估</div>', unsafe_allow_html=True)

# ================= 2. 侧边栏：角色与需求发起 =================
st.sidebar.header("👤 角色与权限管理")
role = st.sidebar.radio("当前登录角色：", ["决策者 (Admin)", "普通浏览者 (User)"])

# 根据角色显示不同的提示语
if role == "决策者 (Admin)":
    st.sidebar.success("✅ 您拥有最高权限：可发起新采集、可下载商业策划案。")
else:
    st.sidebar.info("ℹ️ 您当前为浏览模式：仅可查看数据大盘与赛道排行，无法下载核心文档。")

st.sidebar.markdown("---")
st.sidebar.header("📌 需求发起与控制")

# 只有 Admin 才能发起新采集
if role == "决策者 (Admin)":
    user_query = st.sidebar.text_input("输入想挖掘的 AI 应用方向：", value="AI Agent")
    if st.sidebar.button("🚀 发起新批次采集"):
        with st.sidebar.status("正在执行端到端流水线...", expanded=True) as status:
            st.write("1. 正在从多源渠道采集数据...")
            time.sleep(1.5) 
            st.write("2. 正在进行数据清洗、去重与快照留存...")
            time.sleep(1)
            st.write("3. 正在调用大模型进行机会判别与聚类打分...")
            time.sleep(1.5)
            status.update(label="✅ 新批次分析完成！", state="complete", expanded=False)
        st.success("批次 B02 已生成！请在下方切换查看。")
else:
    st.sidebar.warning("⚠️ 普通浏览者无权发起新需求采集。")

# 多批次下拉菜单
st.sidebar.markdown("---")
selected_batch = st.sidebar.selectbox("📂 切换分析批次：", ["B01 (全量初始数据)", "B02 (最新生成批次)"])

# ================= 3. 读取多批次数据 =================
# 这里模拟了 B01 读取本地真实结果，B02 读取另一套结果或者动态生成演示
@st.cache_data
def load_data(batch):
    try:
        # 为了演示，如果选 B02，我们动态复制一份 B01 的数据改个名字
        # 真实比赛中，你应该让 build_result 脚本生成带 B02 前缀的 CSV 文件
        if batch == "B01 (全量初始数据)":
            df1 = pd.read_csv("result1.csv")
            df2 = pd.read_csv("result2.csv")
            df3 = pd.read_csv("result3.csv")
            df4 = pd.read_csv("result4.csv")
        else:
            df1 = pd.read_csv("result1.csv")
            df2 = pd.read_csv("result2.csv")
            df3 = pd.read_csv("result3.csv")
            df4 = pd.read_csv("result4.csv").head(5) # 演示用，只取前5条
            df4["机会价值分"] = df4["机会价值分"] * 0.9 # 模拟新数据
            df4["主题簇名称"] = "【B02新发现】 " + df4["主题簇名称"]
        return df1, df2, df3, df4
    except Exception as e:
        st.error(f"数据读取失败，请确保 CSV 文件在当前目录。错误：{e}")
        return None, None, None, None

df1, df2, df3, df4 = load_data(selected_batch)

# ================= 4. 核心看板呈现 =================
if df1 is not None:
    st.markdown(f"### 📊 批次【{selected_batch}】核心数据大盘")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("采集记录数", f"{len(df1)} 条")
    col2.metric("真实机会数", f"{len(df2[df2['是否构成机会'] == 1])} 条")
    col3.metric("高价值赛道", f"{len(df3)} 个")
    col4.metric("Top1 赛道", df4.iloc[0]['主题簇名称'][:12] + "..." if not df4.empty else "无")

    st.markdown("---")

    # 图表区
    col_left, col_right = st.columns([1, 1.2])
    with col_left:
        st.markdown("### 🌐 数据来源分布")
        source_counts = df1['来源网站名称'].value_counts().reset_index()
        source_counts.columns = ['来源', '数量']
        fig_pie = px.pie(source_counts, values='数量', names='来源', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.markdown("### 🏢 机会行业分布 TOP 10")
        industry_counts = df2[df2['是否构成机会'] == 1]['所属行业'].value_counts().head(10).reset_index()
        industry_counts.columns = ['行业', '机会数量']
        fig_bar = px.bar(industry_counts, x='机会数量', y='行业', orientation='h', color='机会数量', color_continuous_scale='Teal')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # 排行榜
    st.markdown("### 🏆 高价值赛道排行榜与决策推荐")
    display_cols = ['优先级', '主题簇编号', '主题簇名称', '功能类别', '所属行业', '机会价值分']
    st.dataframe(df4[display_cols].head(15).style.background_gradient(subset=['机会价值分'], cmap='Blues'), use_container_width=True)

    # ================= 5. 权限隔离：决策产出 =================
    st.markdown("---")
    st.markdown("### 📄 商业策划案生成与导出")
    
    if role == "决策者 (Admin)":
        st.markdown('<div class="perm-box">当前角色：【决策者】。您拥有文档导出权限。</div>', unsafe_allow_html=True)
        
        # 模拟挑选最优赛道
        selected_track = st.selectbox("请选择需要导出策划案的赛道：", df4['主题簇名称'].head(5).tolist())
        
        if st.button("📄 生成立项策划案并下载"):
            with st.spinner("大模型正在撰写策划案..."):
                time.sleep(2) # 模拟大模型生成延迟
                mock_content = f"# 《{selected_track}》立项策划案\n\n## 一、目标用户与核心痛点\n本赛道针对..."
                st.success("✅ 策划案已生成！")
                st.download_button("📥 点击下载 Markdown 文档", data=mock_content, file_name="商业策划案.md", mime="text/markdown")
    else:
        st.warning("🔒 权限不足：仅【决策者 (Admin)】角色可生成立项策划案与导出文档。")