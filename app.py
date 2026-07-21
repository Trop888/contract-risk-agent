import streamlit as st
import requests
from core.model import ContractAnalysisResult
from agents.report_generator.word_report import build_word_report

import os
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="合同风险审查助手", page_icon="📄", layout="wide")

# ---- 注入自定义 CSS ----
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 2rem; max-width: 1250px;}
    .stButton>button {border-radius: 8px; font-weight: 600;}
    div[data-testid="stExpander"] {border-radius: 10px; border: 1px solid #E2E8F0;}
    /* 右侧对话栏：固定不随主页面滚动 + 卡片外观 */
    div[data-testid="stHorizontalBlock"] > div:last-child {
        position: sticky;
        top: 1rem;
        align-self: flex-start;
        max-height: calc(100vh - 2rem);
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 10px 16px 16px 16px;
    }
</style>
""", unsafe_allow_html=True)

LEVEL_COLOR = {"高": "#DC2626", "中": "#D97706", "低": "#16A34A"}
LEVEL_EMOJI = {"高": "🔴", "中": "🟠", "低": "🟢"}


def call_analyze(uploaded_files) -> dict:
    files = [("files", (f.name, f.getvalue())) for f in uploaded_files]
    resp = requests.post(f"{API_BASE}/analyze", files=files, timeout=300)
    resp.raise_for_status()
    return resp.json()


def call_chat(question: str, contract_text: str, history: list[dict]) -> str:
    payload = {"question": question, "contract_text": contract_text, "history": history}
    resp = requests.post(f"{API_BASE}/chat", json=payload, timeout=180)
    resp.raise_for_status()
    return resp.json()["answer"]


# ---- 头部（整宽）----
st.markdown("""
<div style="margin-bottom: 12px;">
  <h1 style="margin-bottom:2px; font-size:32px;">📄 合同风险审查助手</h1>
  <p style="color:#64748B; font-size:15px; margin-top:0;">
    上传合同（PDF / Word / TXT / 图片），AI 自动识别风险、匹配法条、生成报告，并支持追问。
  </p>
</div>
""", unsafe_allow_html=True)

# ---- 顶层两栏：左=分析，右=对话（始终存在）----
left, right = st.columns([2, 1], gap="large")

# ========== 左列：上传 + 分析结果 ==========
with left:
    uploaded_files = st.file_uploader(
        "请选择合同文件（可多选：多页照片、合同+附件会合并为一份分析）",
        type=["pdf", "doc", "docx", "txt", "jpg", "png", "jpeg"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        if st.button("🚀 开始分析", type="primary"):
            try:
                with st.spinner("多个 AI Agent 正在协作分析，请稍候..."):
                    data = call_analyze(uploaded_files)
                st.session_state["result"] = ContractAnalysisResult(**data)
                st.session_state["chat_history"] = []
            except requests.exceptions.RequestException as e:
                st.error(f"调用后端失败，请确认后端服务已启动（{API_BASE}）。\n\n{e}")

    if "result" in st.session_state:
        result = st.session_state["result"]

        if not result.is_valid:
            st.warning("⚠️ 无法进行有效审查")
            st.write(result.summary)
        else:
            high = sum(1 for it in result.risk_items if it.level.value == "高")
            mid = sum(1 for it in result.risk_items if it.level.value == "中")
            low = sum(1 for it in result.risk_items if it.level.value == "低")
            overall = result.overall_risk.value
            cards = [
                (overall, "整体风险", LEVEL_COLOR.get(overall, "#2563EB")),
                (str(high), "高风险", "#DC2626"),
                (str(mid), "中风险", "#D97706"),
                (str(low), "低风险", "#16A34A"),
            ]
            cards_html = "".join(
                f"""<div style="flex:1; background:{c}; border-radius:12px; padding:16px 8px; text-align:center; color:#fff;">
                        <div style="font-size:26px; font-weight:700; line-height:1.2;">{v}</div>
                        <div style="font-size:13px; opacity:.92;">{label}</div>
                    </div>"""
                for v, label, c in cards
            )
            st.markdown(f'<div style="display:flex; gap:12px; margin:12px 0 20px 0;">{cards_html}</div>',
                        unsafe_allow_html=True)

            conc_color = LEVEL_COLOR.get(overall, "#2563EB")
            st.markdown(f"""
            <div style="background:#F8FAFC; border-left:5px solid {conc_color}; border-radius:8px;
                        padding:16px 20px; margin-bottom:16px;">
              <div style="font-size:13px; color:#64748B; margin-bottom:6px;">📋 总体结论</div>
              <div style="font-size:15px; line-height:1.7; color:#0F172A;">{result.overall_conclusion}</div>
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label="📥 下载 Word 报告",
                data=build_word_report(result),
                file_name="合同风险审查报告.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

            with st.expander("📝 合同摘要", expanded=True):
                st.write(result.summary)

            st.markdown(f"#### 🔍 发现 {len(result.risk_items)} 项风险")
            for i, item in enumerate(result.risk_items, 1):
                lv = item.level.value
                emoji = LEVEL_EMOJI.get(lv, "⚪")
                with st.expander(f"{emoji} 风险 {i}：{item.risk_type}　（{lv}风险）"):
                    st.markdown(f"**描述：** {item.description}")
                    if item.clause:
                        st.markdown(f"**相关条款：** {item.clause}")
                    if item.suggestion:
                        st.markdown(f"**💡 修改建议：** {item.suggestion}")
                    if item.legal_basis:
                        st.markdown(f"**⚖️ 法律依据：** {item.legal_basis}")

# ========== 右列：对话追问（固定、独立滚动）==========
with right:
    st.markdown("##### 💬 追问合同细节")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    has_result = "result" in st.session_state and st.session_state["result"].is_valid

    # 历史区：独立滚动（与主页面滚动分开）
    history_box = st.container(height=430)
    with history_box:
        if not has_result:
            st.caption("请先在左侧上传并分析合同，然后在这里追问 👈")
        else:
            for msg in st.session_state["chat_history"]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

    # 输入框：钉在面板底部
    question = st.chat_input("例如：违约金多少算合理？", disabled=not has_result)
    if question and has_result:
        result = st.session_state["result"]
        with history_box:
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("思考中..."):
                    answer = call_chat(question, result.contract_text, st.session_state["chat_history"])
                st.markdown(answer)
        st.session_state["chat_history"].append({"role": "user", "content": question})
        st.session_state["chat_history"].append({"role": "assistant", "content": answer})