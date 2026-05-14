import streamlit as st
import pandas as pd
from google import genai

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Prepaid Finance AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------
st.markdown("""
<style>

    .stApp {
        background: linear-gradient(to right, #0b1220, #172033);
        color: #f8fafc;
    }

    .main-title {
        font-size: 42px;
        font-weight: bold;
        color: #4cc9f0;
        text-align: center;
        margin-bottom: 10px;
    }

    .subtitle {
        text-align: center;
        color: #dbeafe;
        margin-bottom: 30px;
        font-size: 18px;
    }

    .success-box {
        background-color: #14532d;
        padding: 12px;
        border-radius: 10px;
        color: #dcfce7;
        font-weight: 600;
        margin-bottom: 20px;
    }

    .answer-box {
        background-color: #111827;
        padding: 20px;
        border-radius: 16px;
        border-left: 6px solid #4cc9f0;
        font-size: 16px;
        line-height: 1.7;
        color: #f8fafc;
        margin-top: 15px;
    }

    .stTextInput > div > div > input {
        background-color: #1e293b;
        color: #f8fafc;
        border-radius: 10px;
        border: 1px solid #64748b;
    }

    section[data-testid="stFileUploader"] {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #475569;
    }

    section[data-testid="stSidebar"] {
        background-color: #020617;
    }

    /* SIDEBAR HEADINGS */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
    }

    /* SIDEBAR TEXT */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #cbd5e1 !important;
    }

    /* INFO BOX */
    div[data-baseweb="notification"] {
        background-color: #172554 !important;
        color: #dbeafe !important;
        border: 1px solid #2563eb !important;
    }

    /* METRICS */
    [data-testid="metric-container"] {
        background-color: #111827;
        border: 1px solid #334155;
        padding: 12px;
        border-radius: 12px;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown('<div class="main-title">💰 Prepaid Expense & Insurance AI</div>', unsafe_allow_html=True)

st.markdown('<div class="subtitle">AI-powered financial workbook assistant using Gemini</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:

    st.markdown("## ⚙️ Instructions")

    st.info("""
    1. Enter Gemini API Key  
    2. Upload Excel Workbook  
    3. Ask financial questions  
    """)

    st.markdown("---")

    st.markdown("## 🎛️ Mode Guide")

    st.markdown("""
    **📊 Workbook Q&A (Strict)**  
    → Answers ONLY from uploaded Excel data

    **🧠 Financial Advisory (Open)**  
    → Uses financial knowledge + workbook insights for advice
    """)

    st.markdown("---")

    st.markdown("## 🚀 Top Features")

    st.markdown("""
    - AI financial Q&A  
    - Auto workbook insights  
    - Smart Excel understanding  
    """)

# ---------------------------------------------------
# API KEY
# ---------------------------------------------------
api_key = st.text_input(
    "🔑 Enter your Gemini API Key",
    type="password",
    placeholder="Paste your API key here..."
)

# ---------------------------------------------------
# FUNCTION: GET BEST MODEL
# ---------------------------------------------------
def get_best_model(client):
    try:
        models = [m.name for m in client.models.list()]

        priority = [
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro"
        ]

        for p in priority:
            if any(p in m for m in models):
                return p

        return models[0] if models else None

    except Exception as e:
        st.error(f"Model fetch failed: {e}")
        return None


# ---------------------------------------------------
# FUNCTION: FIND RELEVANT NUMERIC DATA (KEYWORD BASED)
# ---------------------------------------------------
def extract_relevant_numeric(df, keywords):
    if df is None or df.empty:
        return []

    relevant_values = []

    for col in df.columns:
        col_lower = str(col).lower()

        if any(k in col_lower for k in keywords):
            numeric = pd.to_numeric(df[col], errors="coerce")
            relevant_values.extend(numeric.dropna().tolist())

    return relevant_values


def has_relevant_columns(df_list, keywords):
    for df in df_list:
        for col in df.columns:
            if any(k in str(col).lower() for k in keywords):
                return True
    return False


# ---------------------------------------------------
# APP LOGIC
# ---------------------------------------------------
if api_key:

    try:
        client = genai.Client(api_key=api_key)
        model_name = get_best_model(client)

        if not model_name:
            st.error("❌ No Gemini models available.")
            st.stop()

        st.markdown(f"""
        <div class="success-box">
        ✅ Connected Successfully | Using Model: <b>{model_name}</b>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Connection Error: {e}")
        st.stop()

    # ---------------------------------------------------
    # FILE UPLOADER
    # ---------------------------------------------------
    uploaded_file = st.file_uploader("📂 Upload Excel Workbook", type=["xlsx"])

    if uploaded_file:

        try:
            summary_df = pd.read_excel(uploaded_file, sheet_name="Prepaid Summary")
            expenses_df = pd.read_excel(uploaded_file, sheet_name="Prepaid Expenses")
            insurance_df = pd.read_excel(uploaded_file, sheet_name="Prepaid Insurance")

            st.success("✅ Workbook loaded successfully!")

        except Exception as e:
            st.error(f"Excel Error: {e}")
            st.stop()

        # ---------------------------------------------------
        # KEYWORD-BASED DETECTION
        # ---------------------------------------------------
        keywords = [
            "amount", "value", "balance", "total",
            "expense", "insurance", "prepaid"
        ]

        has_financial_data = has_relevant_columns(
            [summary_df, expenses_df, insurance_df],
            keywords
        )

        # ---------------------------------------------------
        # FINANCIAL SUMMARY (ONLY IF RELEVANT DATA EXISTS)
        # ---------------------------------------------------
        if has_financial_data:

            summary_numbers = extract_relevant_numeric(summary_df, keywords)
            expense_numbers = extract_relevant_numeric(expenses_df, keywords)
            insurance_numbers = extract_relevant_numeric(insurance_df, keywords)

            if summary_numbers or expense_numbers or insurance_numbers:

                total_summary = sum(summary_numbers)
                total_expenses = sum(expense_numbers)
                total_insurance = sum(insurance_numbers)

                st.markdown("## 📈 Financial Summary")

                kpi1, kpi2, kpi3 = st.columns(3)

                with kpi1:
                    st.metric("Total Summary Value", f"{total_summary:,.2f}")

                with kpi2:
                    st.metric("Total Expense Value", f"{total_expenses:,.2f}")

                with kpi3:
                    st.metric("Total Insurance Value", f"{total_insurance:,.2f}")

                st.markdown("<br>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Summary Rows", len(summary_df))

                with col2:
                    st.metric("Expense Records", len(expenses_df))

                with col3:
                    st.metric("Insurance Records", len(insurance_df))

                st.markdown("<br>", unsafe_allow_html=True)

        # ---------------------------------------------------
        # COMMONLY ASKED QUESTIONS
        # ---------------------------------------------------
        st.markdown("## ❓ Commonly Asked Questions")

        st.markdown("""
        - What is the total prepaid expense for this period?  
        - How much insurance is still unamortized?  
        - What is the overall prepaid balance across all sheets?  
        """)

        # ---------------------------------------------------
        # MODE SELECTION
        # ---------------------------------------------------
        st.markdown("## 🎛️ Choose Mode")

        mode = st.radio(
            "Select how AI should respond",
            ["📊 Workbook Q&A (Strict)", "🧠 Financial Advisory (Open)"],
            horizontal=True
        )

        # ---------------------------------------------------
        # QUESTION INPUT
        # ---------------------------------------------------
        st.markdown("## 💬 Ask Financial Questions")

        question = st.text_input(
            "Ask anything about the workbook",
            placeholder="Example: What is the total prepaid balance in April?"
        )

        # ---------------------------------------------------
        # AI RESPONSE
        # ---------------------------------------------------
        if question:

            context = f"""
PREPAID SUMMARY:
{summary_df.head(15).to_string(index=False)}

PREPAID EXPENSES:
{expenses_df.head(15).to_string(index=False)}

PREPAID INSURANCE:
{insurance_df.head(15).to_string(index=False)}
"""

            if mode == "📊 Workbook Q&A (Strict)":

                prompt = f"""
You are a strict financial accounting assistant.

RULES:
- Use ONLY the provided workbook data
- Do NOT use outside knowledge
- If data is not available, say "Not available in workbook"
- Be precise and factual only

DATA:
{context}

QUESTION:
{question}
"""

            else:

                prompt = f"""
You are a senior financial analyst and advisor.

RULES:
- You may use general financial knowledge
- Use workbook data if relevant
- Provide insights, interpretation, and advice
- Highlight risks, trends, and recommendations

WORKBOOK DATA:
{context}

QUESTION:
{question}
"""

            with st.spinner("🤖 Analyzing workbook..."):

                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )

                    st.markdown("## 🧠 AI Answer")

                    st.markdown(f"""
                    <div class="answer-box">
                    {response.text}
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"LLM Error: {e}")

else:
    st.info("👈 Enter your Gemini API key to begin")