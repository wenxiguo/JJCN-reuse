import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 页面标题
st.title("图片对比及键盘标注工具 - CSV版")
st.write("上传包含 'imgurl_A' 和 'imgurl_B' 列的 CSV，使用 ←/→ 浏览，1=是，0=否。")

# 初始化 session_state
ss = st.session_state
if 'current_index' not in ss:
    ss.current_index = 0
if 'labels' not in ss:
    ss.labels = {}
# 用于接收 JS 传来的按键信息
if 'key_event' not in ss:
    ss.key_event = ""

# 上传 CSV
uploaded = st.file_uploader("上传 CSV", type="csv")
if uploaded:
    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.strip()
    n = len(df)
    st.write(f"共 {n} 对图片")

    # 隐藏的侧边栏 text_input，用来承载 JS 传回的按键
    st.sidebar.text_input("hidden", key="key_event", value="", label_visibility="collapsed")
    # 隐藏 sidebar 中的所有输入框
    st.sidebar.markdown(
        """<style>[data-testid="stSidebar"] input {display:none;}</style>""",
        unsafe_allow_html=True,
    )

    # 侧边栏导出
    st.sidebar.header("导出")
    if st.sidebar.button("导出标注结果"):
        labels = [ss.labels.get(i, "") for i in range(n)]
        df['label'] = labels
        data = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("下载 CSV", data, "labeled.csv", "text/csv")

    # 监听到按键事件后，更新状态并重置 key_event
    e = ss.key_event
    if e:
        if e == "left":
            ss.current_index = max(0, ss.current_index - 1)
        elif e == "right" or e in ("1", "0"):  # 标注后跳下一张
            if e == "1":
                ss.labels[ss.current_index] = "是"
            elif e == "0":
                ss.labels[ss.current_index] = "否"
            ss.current_index = min(n - 1, ss.current_index + 1)
        ss.key_event = ""
        st.experimental_rerun()

    # 显示当前图片
    idx = ss.current_index
    row = df.iloc[idx]
    st.write(f"### {idx+1}/{n}")
    c1, c2 = st.columns(2)
    c1.image(row["imgurl_A"], caption="A", use_column_width=True)
    c2.image(row["imgurl_B"], caption="B", use_column_width=True)

    st.write("按 **1** 标“是”，**0** 标“否”，**←/→** 翻页。")
    st.write("当前标注：", ss.labels.get(idx, "未标注"))

    # 注入 JS：将键盘事件写入 sidebar 隐藏输入框
    components.html(
        """
        <script>
        const input = parent.document.querySelector('[data-testid="stSidebar"] input');
        document.addEventListener('keydown', e => {
            let v = "";
            if (e.key === 'ArrowLeft') v = 'left';
            else if (e.key === 'ArrowRight') v = 'right';
            else if (e.key === '1') v = '1';
            else if (e.key === '0') v = '0';
            if (v) {
                input.value = v;
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
        </script>
        """,
        height=0,
    )