
# utils/rag_utils.py
import streamlit as st
import os, json
from groq import Groq
from utils.rag_pdf_utils import load_pdf_bytes, simple_text_split, embed_texts, build_faiss_index, retrieve_top_k

# ================================
#  File to Store Persistent History
# ================================
HISTORY_FILE = "data/rag_history.json"


# ================================
#  Load / Save Persistent History
# ================================
def save_history(username, query, answer):
    """Save question-answer pair to rag_history.json for a user"""
    if not os.path.exists(HISTORY_FILE):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, "w") as f:
            json.dump({}, f)

    with open(HISTORY_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    if username not in data:
        data[username] = []
    data[username].append({"query": query, "answer": answer})

    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_history(username):
    """Load user history from rag_history.json"""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    return data.get(username, [])


def delete_history(username):
    """Delete user history"""
    if not os.path.exists(HISTORY_FILE):
        return
    with open(HISTORY_FILE, "r") as f:
        data = json.load(f)
    if username in data:
        del data[username]
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ================================
#  RAG Reader Page
# ================================
def rag_reader_page():
    st.title("📚 Medical Report Analyzer (RAG PDF Reader)")
    st.markdown("This tool uses **RAG (Retrieval-Augmented Generation)** to answer medical questions based on uploaded reports.")
    st.markdown("Upload a medical report, process it, then ask **multiple questions in a conversation.**")

    # ✅ Initialize in-session memory for conversation
    if "rag_history_buffer" not in st.session_state:
        st.session_state.rag_history_buffer = []

    # =============================
    # STEP 1: Upload PDF and Process
    # =============================
    chunk_size = st.number_input("Chunk Size", min_value=100, max_value=5000, value=1000, step=100)
    overlap = st.number_input("Chunk Overlap", min_value=0, max_value=chunk_size-1, value=200, step=50)
    uploaded_files = st.file_uploader("📎 Upload PDF Files", type=["pdf"], accept_multiple_files=True)

    if st.button("🛠️ Process PDFs"):
        if uploaded_files:
            all_texts = []
            for f in uploaded_files:
                pdf_text = load_pdf_bytes(f.read())
                st.success(f"✅ Extracted text from: {f.name}")
                chunks = simple_text_split(pdf_text, chunk_size, overlap)
                st.info(f"📄 {len(chunks)} chunks created from {f.name}")
                all_texts += chunks

            # STEP 2: Create Embeddings
            embeddings = embed_texts(all_texts)
            index, dim = build_faiss_index(embeddings)

            st.session_state.docs = all_texts
            st.session_state.index = index
            st.session_state.built = True

            # Reset conversation buffer after new PDF processing
            st.session_state.rag_history_buffer = []

            st.success(f"✅ Index built successfully with {len(all_texts)} chunks!")
        else:
            st.error("❌ Please upload at least one PDF.")

    # =============================
    # STEP 2.5: Clear Index
    # =============================
    if st.button("🧹 Clear Index"):
        st.session_state.docs = None
        st.session_state.index = None
        st.session_state.built = False
        st.session_state.rag_history_buffer = []
        st.success("🧽 Index cleared successfully.")

    # =============================
    # STEP 3: Ask Questions with Memory
    # =============================
    if st.session_state.get("built"):
        st.markdown("### 💬 Ask Questions Based on Uploaded Documents")
        query = st.text_input("Your question:")

        if st.button("Ask") and query.strip():
            # STEP 4: Retrieve Top Matches
            st.info("🔍 Retrieving top relevant chunks...")
            results = retrieve_top_k(query, st.session_state.docs, st.session_state.index)
            context = "\n\n".join([r["chunk"] for r in results])
            st.success(f"✅ Retrieved {len(results)} relevant chunks")

            # STEP 5: Send Context + Conversation History + Question to LLM
            st.info("🧠 Sending context and conversation to LLM...")

            SYSTEM_PROMPT = """You are a Medical Report Analysis Assistant using RAG.
            Use the provided medical report context and previous messages to answer the current question.
            Always provide clear, structured, and safe medical explanations.
            If the answer is not in the context, say so politely."""

            client = Groq(api_key=os.getenv("GROQ_API_KEY", st.secrets.get("GROQ_API_KEY")))

            # Combine system message + previous messages + new query
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.rag_history_buffer + [
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}"}
            ]

            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages
            )
            answer = resp.choices[0].message.content.strip()

            # STEP 6: Display answer
            st.subheader("🩺 Answer")
            st.success(answer)

            # STEP 7: Update conversation buffer
            st.session_state.rag_history_buffer.append({"role": "user", "content": query})
            st.session_state.rag_history_buffer.append({"role": "assistant", "content": answer})

            # STEP 8: Save persistent history (per user)
            save_history(st.session_state.username, query, answer)

    # =============================
    # STEP 4: Show Current Conversation
    # =============================
    st.subheader("🧵 Current Conversation (In-Session Memory)")
    if st.session_state.rag_history_buffer:
        for msg in st.session_state.rag_history_buffer:
            role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
            st.markdown(f"**{role}:** {msg['content']}")
    else:
        st.info("No conversation yet.")

    # Clear current in-session conversation
    if st.button("🧹 Clear Current Conversation"):
        st.session_state.rag_history_buffer = []
        st.success("Conversation cleared.")
        # st.rerun()

    # =============================
    # STEP 5: Show Persistent History
    # =============================
    st.subheader("📜 Previous Questions & Answers")
    history = load_history(st.session_state.username)
    if history:
        for entry in reversed(history):
            st.markdown(f"**❓ Q:** {entry['query']}")
            st.markdown(f"**💬 A:** {entry['answer']}")
    else:
        st.info("No previous questions yet.")

    # Download persistent history
    if history:
        st.download_button(
            label="📥 Download History",
            data=json.dumps(history, indent=4),
            file_name="rag_history.json",
            mime="application/json"
        )

    # Delete persistent history
    if history and st.button("🗑️ Delete History"):
        delete_history(st.session_state.username)
        st.success("History deleted successfully.")
        st.session_state.page = "rag"
        st.session_state.rag_history_buffer = []
        st.success("Conversation cleared.")
        st.rerun()
        st.rerun()

















