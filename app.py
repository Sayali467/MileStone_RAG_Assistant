import streamlit as st
from query_engine import query_rag_engine
import config

# Set page config
st.set_page_config(
    page_title="Groww Genie | AI Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Premium custom CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap');
    
    /* Font styling overrides */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #171b1f !important;
        color: #f0f1f5 !important;
    }
    
    /* Main App Background Override */
    .stApp {
        background-color: #171b1f;
    }
    
    /* Sidebar Override */
    [data-testid="stSidebar"] {
        background-color: #1f2327 !important;
        border-right: 1px solid #485650;
    }
    
    /* Heading Font */
    h1, h2, h3, .groww-genie-title {
        font-family: 'Manrope', sans-serif;
    }
    
    /* Groww Genie Title */
    .groww-genie-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f0f1f5;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.2rem;
        justify-content: center;
    }
    .badge-facts {
        background-color: #3c4045;
        border: 1px solid rgba(68, 237, 183, 0.3);
        color: #44edb7;
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 9999px;
        font-weight: 600;
        vertical-align: middle;
        margin-left: 8px;
    }
    .subtitle {
        font-size: 1rem;
        color: #c5d2ca;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Glassmorphic Compliance Sidebar Box */
    .sidebar-disclaimer-card {
        background: #93000a;
        border: 1px solid rgba(255, 180, 171, 0.2);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        color: #ffdad6;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    
    /* Custom Styling for Chat Messages */
    .user-bubble {
        background-color: #00d09c;
        color: #00533c;
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 4px 18px;
        margin-bottom: 1rem;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        font-weight: 500;
    }
    
    .assistant-bubble-container {
        display: flex;
        gap: 16px;
        margin-bottom: 1rem;
        max-width: 85%;
    }
    
    .assistant-avatar {
        height: 32px;
        width: 32px;
        border-radius: 8px;
        background-color: #2e3237;
        border: 1px solid #485650;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 18px;
    }
    
    .assistant-bubble {
        background-color: #2e3237;
        color: #f0f1f5;
        border: 1px solid rgba(72, 86, 80, 0.5);
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 18px 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        flex-grow: 1;
    }
    
    .citation-container {
        margin-top: 1rem;
        font-size: 0.8rem;
        border-top: 1px solid rgba(72, 86, 80, 0.3);
        padding-top: 0.8rem;
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        align-items: center;
    }
    
    .citation-link {
        color: #44edb7;
        text-decoration: none;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .citation-link:hover {
        text-decoration: underline;
    }
    
    .citation-date {
        color: #c5d2ca;
        font-size: 0.8rem;
    }
    
    /* Interactive Example Question Buttons style override */
    div.stButton > button {
        background-color: #24282c !important;
        color: #c5d2ca !important;
        border: 1px solid #485650 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        text-align: left !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.85rem !important;
    }
    
    div.stButton > button:hover {
        border-color: #44edb7 !important;
        color: #44edb7 !important;
        transform: translateY(-2px);
    }
    
    /* Chat Input Override */
    [data-testid="stChatInput"] {
        background-color: #3a3e43 !important;
        border-color: #485650 !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #f0f1f5 !important;
    }
    
    /* Sidebar List Items styling */
    .sidebar-link {
        font-size: 0.85rem;
        color: #c5d2ca;
        text-decoration: none;
        display: block;
        margin-bottom: 0.6rem;
        padding: 0.4rem 0;
    }
    .sidebar-link:hover {
        color: #44edb7;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR CONTENT -----------------
with st.sidebar:
    st.markdown('<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 24px;"><span style="font-size: 24px;">✨</span><h2 style="margin: 0; color: #44edb7;">Groww Genie</h2></div>', unsafe_allow_html=True)
    
    # High-Visibility Disclaimer Sidebar card
    st.markdown(
        '<div class="sidebar-disclaimer-card">'
        '<strong>⚠️ Compliance Disclaimer:</strong><br>'
        'This chatbot operates exclusively on a facts-only scope. '
        'It is strictly prohibited from providing investment advice, comparing schemes, or predicting returns.'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("<h3 style='color: #c5d2ca; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;'>🌐 Scoped Schemes</h3>", unsafe_allow_html=True)
    st.markdown(
        f'<a href="{config.SCHEME_URLS["nippon_india_large_cap"]}" target="_blank" class="sidebar-link">🔹 Nippon India Large Cap Fund</a>'
        f'<a href="{config.SCHEME_URLS["nippon_india_flexi_cap"]}" target="_blank" class="sidebar-link">🔹 Nippon India Flexi Cap Fund</a>'
        f'<a href="{config.SCHEME_URLS["nippon_india_growth_mid_cap"]}" target="_blank" class="sidebar-link">🔹 Nippon India Growth Fund</a>'
        f'<a href="{config.SCHEME_URLS["nippon_india_small_cap"]}" target="_blank" class="sidebar-link">🔹 Nippon India Small Cap Fund</a>'
        f'<a href="{config.SCHEME_URLS["nippon_india_silver_etf_fof"]}" target="_blank" class="sidebar-link">🔹 Nippon India Silver ETF FoF</a>'
        f'<a href="{config.SCHEME_URLS["nippon_india_statements"]}" target="_blank" class="sidebar-link">🔹 Nippon India Statement Portal</a>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.caption("Active model: BGE-Small-en + Groq Llama-3.3-70B")

# ----------------- MAIN UI -----------------
st.markdown(
    '<div class="groww-genie-title">'
    'Groww Genie <span class="badge-facts">✔️ Facts only • No advice</span>'
    '</div>', 
    unsafe_allow_html=True
)
st.markdown('<div class="subtitle">Your mutual fund fact assistant. Ask me anything about ratios, loads, or performance.</div>', unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Trigger handle query
def handle_query(query: str):
    if query:
        # Append User Message
        st.session_state.messages.append({"role": "user", "text": query})
        
        # Get Response
        with st.spinner("Retrieving facts from context database..."):
            res = query_rag_engine(query)
            
        # Append Bot Response
        st.session_state.messages.append({
            "role": "assistant",
            "text": res["answer"],
            "citation": res.get("citation_url", ""),
            "last_updated": res.get("last_updated", "")
        })

# Example questions in a columns layout
st.write("")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("What is the expense ratio of Nippon India Large Cap Fund?", key="q1"):
        handle_query("What is the expense ratio of Nippon India Large Cap Fund?")

with col2:
    if st.button("What are the exit load details for Nippon India Flexi Cap Fund?", key="q2"):
        handle_query("What are the exit load details for Nippon India Flexi Cap Fund?")

with col3:
    if st.button("How can I download my capital gains statement?", key="q3"):
        handle_query("How can I download my capital gains statement?")

st.write("---")

# Render Conversation Logs
chat_placeholder = st.container()
with chat_placeholder:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">{msg["text"]}</div>', unsafe_allow_html=True)
        else:
            # Assistant bubble uses an icon container and content block similar to the design mock
            bubble_html = f'''
            <div class="assistant-bubble-container">
                <div class="assistant-avatar">✨</div>
                <div class="assistant-bubble">
                    <div style="line-height: 1.6; margin-bottom: 0.5rem;">{msg["text"]}</div>
            '''
            
            if msg.get("citation"):
                bubble_html += f'''
                    <div class="citation-container">
                        <a href="{msg["citation"]}" target="_blank" class="citation-link">🔗 Source Link</a>
                '''
                if msg.get("last_updated"):
                    bubble_html += f'<span class="citation-date">📅 Last updated: {msg["last_updated"]}</span>'
                bubble_html += '</div>'
                
            bubble_html += '</div></div>'
            st.markdown(bubble_html, unsafe_allow_html=True)

# Chat Input field
user_input = st.chat_input("Ask a factual question about scoped Nippon India schemes...")
if user_input:
    handle_query(user_input)
    st.rerun()
