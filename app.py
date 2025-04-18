import streamlit as st
import pandas as pd

st.set_page_config(page_title="图片对比及标签工具")
st.title("🖼️ 图片对比及标签工具")
st.write("上传 CSV，需包含 `imgurl_A` 和 `imgurl_B` 两列。")

# ─── Session State 初始化 ───────────────────────────
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'labels' not in st.session_state:
    st.session_state.labels = {}

# ─── 上传并缓存 CSV ────────────────────────────────────
uploaded = st.file_uploader("上传 CSV 文件", type="csv")
if uploaded:
    if 'df' not in st.session_state or st.session_state.uploaded_file != uploaded:
        df = pd.read_csv(uploaded)
        df.columns = df.columns.str.strip()
        if not {'imgurl_A', 'imgurl_B'}.issubset(df.columns):
            st.error("CSV 必须包含 imgurl_A 和 imgurl_B 两列")
            st.stop()
        st.session_state.df = df
        st.session_state.uploaded_file = uploaded
    df = st.session_state.df
else:
    st.info("请先上传 CSV 文件")
    st.stop()

# ─── 基本参数 ─────────────────────────────────────────
total = len(df)
idx = st.session_state.current_index

done = sum(1 for v in st.session_state.labels.values() if v in ("是", "否"))

# ─── 侧边栏：进度 & 导出 ─────────────────────────────
with st.sidebar:
    st.header("进度 & 导出")
    metric_placeholder = st.empty()
    progress_placeholder = st.empty()
    metric_placeholder.metric("已标注 / 总共", f"{done} / {total}")
    progress_placeholder.progress(done / total)
    if st.button("导出标注结果"):
        out = df.copy()
        out['label'] = [st.session_state.labels.get(i, "") for i in range(total)]
        csv_bytes = out.to_csv(index=False).encode('utf-8')
        st.download_button("下载 CSV", data=csv_bytes, file_name="labeled.csv", mime="text/csv")

# ─── 图片展示（固定尺寸） ─────────────────────────────────
row = df.iloc[idx]
c1, c2 = st.columns(2)
fixed_w, fixed_h = 400, 400  # 固定显示尺寸
html_template = f"""
<div style="width:{fixed_w}px;height:{fixed_h}px;border:1px solid #ccc;display:flex;align-items:center;justify-content:center;">
  <img src="{{url}}" style="max-width:100%;max-height:100%;object-fit:contain;" />
</div>
"""
with c1:
    st.markdown(html_template.format(url=row.imgurl_A), unsafe_allow_html=True)
    st.caption("图片 A")
with c2:
    st.markdown(html_template.format(url=row.imgurl_B), unsafe_allow_html=True)
    st.caption("图片 B")

# ─── 当前标注状态 ─────────────────────────────────────
status = st.session_state.labels.get(idx, "")
if status == "":
    st.info("⏳ 尚未标注")
elif status == "是":
    st.success("✅ 已标注：是")
else:
    st.warning("❌ 已标注：否")

st.markdown("---")

# ─── 回调函数 ─────────────────────────────────────────
def mark(label):
    st.session_state.labels[st.session_state.current_index] = label
    if st.session_state.current_index < total - 1:
        st.session_state.current_index += 1

def go_prev():
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1

def go_next():
    if st.session_state.current_index < total - 1:
        st.session_state.current_index += 1

# ─── 操作按钮 ─────────────────────────────────────────
col_yes, col_no = st.columns(2)
col_yes.button("✅ 是", key=f"yes_{idx}", on_click=mark, args=("是",))
col_no.button("❌ 否", key=f"no_{idx}", on_click=mark, args=("否",))
st.markdown("---")
col_prev, col_next = st.columns(2)
col_prev.button("⬅️ 上一张", on_click=go_prev)
col_next.button("➡️ 下一张", on_click=go_next)
