import streamlit as st
import pandas as pd

st.title("图片对比及标签工具 - CSV版")
st.write("请上传一个 CSV 文件，文件中应包含 'imgurl_A' 和 'imgurl_B' 两列，每行对应一对图片的地址。")

# 初始化 session_state，用于保存当前图片索引、各行的标注以及重跑标志
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'labels' not in st.session_state:
    st.session_state.labels = {}
if 'need_rerun' not in st.session_state:
    st.session_state.need_rerun = False

# 上传 CSV 文件
uploaded_file = st.file_uploader("上传 CSV 文件", type=["csv"])
if uploaded_file is not None:
    # 读取 CSV 文件，并去除列名前后空格
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    total_rows = len(df)
    st.write(f"共 {total_rows} 对图片")
    st.dataframe(df)

    # 侧边栏始终显示导出按钮，方便随时导出当前标注结果
    st.sidebar.header("导出标注结果")
    if st.sidebar.button("导出当前标注结果"):
        # 对于未标注的行保留空白，标注了的显示“是”或“否”
        labels_list = [st.session_state.labels.get(i, "") for i in range(total_rows)]
        df['label'] = labels_list
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("点击下载 CSV 文件", csv_data,
                                   file_name="labeled_data.csv", mime="text/csv")

    st.write("### 开始对图片进行对比和标注")

    current_index = st.session_state.current_index
    row = df.iloc[current_index]
    st.write(f"#### 图片对比 {current_index + 1} / {total_rows}")

    col1, col2 = st.columns(2)
    with col1:
        st.image(row['imgurl_A'], caption="图片 A", use_column_width=True)
    with col2:
        st.image(row['imgurl_B'], caption="图片 B", use_column_width=True)

    st.markdown("### 请点击下方按钮进行标注（标注后自动跳转到下一对图片）")

    # 定义标注回调函数，不直接调用 experimental_rerun，而是设置一个标志
    def mark_and_jump(label):
        st.session_state.labels[st.session_state.current_index] = label
        if st.session_state.current_index < total_rows - 1:
            st.session_state.current_index += 1
        st.session_state.need_rerun = True

    mark_col1, mark_col2 = st.columns(2)
    mark_col1.button("是", on_click=mark_and_jump, args=("是",), key=f"yes_{current_index}")
    mark_col2.button("否", on_click=mark_and_jump, args=("否",), key=f"no_{current_index}")

    st.markdown("---")
    st.write("### 导航")
    nav_col1, nav_col2 = st.columns(2)
    if nav_col1.button("上一张"):
        if st.session_state.current_index > 0:
            st.session_state.current_index -= 1
        st.experimental_rerun()
    if nav_col2.button("下一张"):
        if st.session_state.current_index < total_rows - 1:
            st.session_state.current_index += 1
        st.experimental_rerun()

    # 自动重跑逻辑：检查标注按钮回调后是否需要自动跳转
    if st.session_state.need_rerun:
        st.session_state.need_rerun = False
        st.experimental_rerun()
