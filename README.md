# YouTranscribe • Full-Length YouTube Video to Text Transcriber (Streamlit Edition)

YouTranscribe is a pure-Python **Streamlit** web application designed to take any YouTube video link and transcribe the video into text for its **entire duration** (from 0:00 to the very end). It provides instant, timestamped, continuous, exportable transcripts with interactive playback, automatic file logging, and Hinglish-to-English script conversion.

---

## 🌟 Key Features

* **Full-Length Transcription**:
  * Transcribes 100% of the video duration, from 1-minute shorts to multi-hour lectures, podcasts, and interviews.
  * Direct InnerTube Android Gateway engine that fetches full transcripts in 1–3 seconds without downloading video/audio files.
* **Smart Language Selection & Hinglish-to-English Converter**:
  * **Language Selector**: Choose between `Auto (Keep Spoken Language)`, `English`, `Hindi`, `Spanish`, `French`, or `German`.
  * **Hinglish-to-English Converter**: Automatically converts Devanagari ASR phonemes into readable Latin English words (`यू नो आई वास वाचिंग...` ➔ `you know I was watching...`).
  * **1-Click Script Switcher**: Easily toggle between readable English script and original Devanagari script.
* **Automatic File Logging & Versioning in `content/`**:
  * Every completed transcript is automatically saved to `content/<Video Title>.txt`.
  * **Content Identity Check**: Hashes content with SHA-256 to avoid duplicating identical transcripts, and increments version suffixes when content differs.
* **Sentence & Speaker Line Breaking**:
  * Formatted continuous text cleanly breaks onto a new line after every terminal punctuation mark (`.`, `?`, `!`, `।`).
  * Protects abbreviations (`Dr.`, `Mr.`, `U.S.`, `etc.`), initials, and decimals from false breaks.
  * Detects speaker transitions (`SPEAKER:`, `>>`, `[Host]:`).
* **Multi-View Workspace**:
  * **💬 Timestamped Transcript**: Conversational paragraphs paired with time badges.
  * **📄 Continuous Clean Text**: Flowing text formatted for AI models (ChatGPT, Claude, Gemini) or study notes.
  * **📥 Export Formats**: 1-click downloads for `.TXT`, `.SRT` (subtitles), `.VTT`, and structured `.JSON`.
  * **📊 Overview & Highlights**: Summary stats, reading time, and timeline milestones.
* **📁 Sidebar Saved Transcripts Explorer**:
  * Instantly browse, view, and re-download previously saved transcripts directly from the sidebar.

---

## 🏗️ Architecture

```
d:\AI\transcribe/
├── app.py                 # Pure-Python Streamlit application (UI + InnerTube engine)
├── requirements.txt       # Python dependencies (streamlit, requests, indic-transliteration, etc.)
├── run.bat                # 1-click Windows launcher (Local or Tunnel mode)
├── deployment-strategies/ # Comprehensive Cloud Deployment Guides & Decision Matrix
│   ├── AWS_Deployment.md
│   ├── Azure_Deployment.md
│   ├── GCP_Deployment.md
│   └── Conclusion.md
├── content/               # Auto-logged video transcripts (<Video Title>.txt)
│   ├── .gitkeep
│   └── <Video Title>.txt
└── README.md              # Project documentation
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
Simply double-click [`run.bat`](file:///d:/AI/transcribe/run.bat) (or run `streamlit run app.py`).

`run.bat` allows you to choose:
* **Option 1 (Default)**: Launch locally on **`http://localhost:8501`**.
* **Option 2**: Launch locally and expose a secure public HTTPS tunnel to open on your phone or share with others.
