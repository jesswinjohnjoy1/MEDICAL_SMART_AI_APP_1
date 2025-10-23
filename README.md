🧠 Medical Smart AI Assistant
This project is an AI-powered medical assistant web application built with Streamlit, LLM integration, and RAG (Retrieval-Augmented Generation).
It provides two main features:

💬 Medical Chatbot — An intelligent chatbot that answers only medical-related queries.

📚 RAG PDF Reader — Upload medical documents (PDFs) and ask questions directly from their content.

🚀 Features

🔐 User Authentication System

Sign up, login, and forgot password functionality.

Session timeout with secure JWT token-based authentication.

🧠 LLM-Powered Medical Chatbot

Integrated with Groq API (llama-3.3-70b-versatile model).

Answers only medically relevant questions in Markdown format.

Chat session history stored in SQLite.

📄 PDF RAG System

Upload medical PDFs.

Automatic text chunking and embedding using sentence-transformers + FAISS.

Ask questions and retrieve contextually relevant answers from uploaded files.

🗂️ Persistent Storage

SQLite database (data/smartai.db) for users, chat sessions, documents, and RAG history.

🧰 Clean Codebase

Modular structure (utils/ folder for separate logic).

JWT authentication & session management.

🧭 Project Structure
.
├── app.py                    # Main Streamlit app
├── requirements.txt          # Python dependencies
├── utils/
│   ├── auth_utils.py         # Signup / Login / Forgot password
│   ├── chatbot_utils.py      # Chatbot page with LLM integration
│   ├── db.py                 # SQLite database connection & models
│   ├── rag_pdf_utils.py      # RAG processing (PDF + embeddings)
│   └── rag_utils.py          # Used inside app for RAG page
├── data/
│   ├── smartai.db            # SQLite database (auto-created)
│   └── users.json            # Optional auth storage file
├── view_data.py              # Script to view database
└── README.md

🧪 Prerequisites

🐍 Python 3.9 or above

A valid Groq API Key

Internet connection for the LLM API

pip for installing dependencies

📦 Installation
# 1️⃣ Clone the repository
git clone https://github.com/jesswinjohnjoy1/MEDICAL_SMART_AI_APP_1
cd MEDICAL_SMART_AI_APP_1

# 2️⃣ Create a virtual environment
python -m venv venv
# On macOS / Linux
source venv/bin/activate
# On Windows
venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

🔑 Add Your API Key

Create a file named .streamlit/secrets.toml in the project root:

GROQ_API_KEY = "your_groq_api_key_here"


▶️ Run the Application
streamlit run app.py


Then open the URL displayed in your terminal (usually http://localhost:8501).

👤 User Authentication

Sign Up with username, password, and secret question/answer.

Login to access the chatbot and RAG PDF Reader.

Forgot Password recovery via secret question.

JWT tokens maintain session validity.

🧠 Chatbot Usage

Navigate to 💬 Chatbot after logging in.

Type your medical-related question in the text box.

The bot classifies medical instruments into categories such as:

Diagnostic

Surgical

Laboratory

Therapeutic

Imaging

Patient Monitoring

Dental

For non-medical queries, the chatbot responds:

"Sorry, I can only answer medical-related questions."

📚 RAG PDF Reader Usage

Go to 📚 RAG PDF Reader.

Upload a medical document (PDF).

Ask natural language questions about the content.

The system retrieves relevant text chunks using FAISS vector search.

🛡️ Security Notes

Passwords are securely hashed using Werkzeug.

JWT tokens ensure session expiration after 30 minutes.

API keys are stored in st.secrets for safety.

🧰 Tech Stack
Component	Technology
🖥 Frontend / UI	Streamlit
🧠 Backend	Python
🗃 Database	SQLite
🧬 Embeddings	Sentence Transformers (all-MiniLM-L6-v2)
📈 Vector Index	FAISS
🤖 LLM API	Groq
🔐 Authentication	JWT + password hashing
🌐 Live Demo

medical-smart-ai-app-1.streamlit.app

✅ Tip:

Use a .env or .toml file to manage secrets securely.

Commit only necessary files and add venv/ and sensitive files to .gitignore.
