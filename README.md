# Municipal Engineering AI Chatbot
## ECE 570 Course Project - Track 2 Product Prototype

### Project Overview
This project is a Retrieval-Augmented Generation (RAG) system that answers municipal engineering policy questions using only the content of the official Engineering Policy Manual. The system is designed to provide accurate, citation-grounded answers while properly refusing to answer questions that fall outside the scope of the manual.

The system is deployed as a web application using Streamlit and uses ChromaDB for vector storage, the all-MiniLM-L6-v2 sentence transformer for embeddings, and the Claude API for answer generation.

---

### Live Deployment
The application is currently deployed and accessible at:
https://ece570-class-project-engineering-ai-assistant-gvtxjsbgzc6pkujc.streamlit.app/

---

### Code and Materials
This project is split across two locations:

**GitHub Repository (Streamlit deployment code):**
https://github.com/blackb46/ece570-class-project-engineering-ai-assistant

Contains:
- `engineering.py` - the deployed Streamlit web application
- `requirements.txt` - Python dependencies for Streamlit Cloud
- `README.md` - this file
- `vectorstore/` - pre-built ChromaDB index built from the Engineering Policy Manual using Config B (400/75)

**Google Drive (Colab development notebook and evaluation files):**
https://drive.google.com/drive/folders/1lIahiHz681nWmhUoXTqvCxo4174GzAIn?usp=sharing

Contains:
- `Engineering_AI_Chatbot_CP2.ipynb` - full development and evaluation notebook
- `evaluation_questions.csv` - 50-question test bank used for evaluation
- `baseline_evaluation_results.csv` - CP1 baseline 50-question evaluation results
- `cp2_evaluation_results.csv` - CP2 four-configuration experiment results (200 scored answers)
- `data/Engineering_Manual.docx` - source policy manual used to build the corpus
- `Checkpoint_01_Backup/` - CP1 code and results preserved for reference

---

### Repository Structure
```
engineering.py          # Main Streamlit web application
requirements.txt        # Python dependencies
README.md               # This file
vectorstore/            # ChromaDB persistent vector database folder
chroma.sqlite3          # Vector index built from the Engineering Policy Manual
```

---

### Dependencies
All dependencies are listed in requirements.txt and installed automatically by Streamlit Cloud.

To run locally, install dependencies with:
```
pip install -r requirements.txt
```

Required libraries:
- streamlit - web interface
- anthropic - Claude API for answer generation
- chromadb - vector database for similarity search
- sentence-transformers - text embedding model
- python-docx - Word document parsing (used in Colab notebook)
- pandas - evaluation results handling (used in Colab notebook)
- protobuf==3.20.3 - pinned to resolve compatibility issue with chromadb

---

### How to Run Locally
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.streamlit/secrets.toml` file with your Claude API key:
```
CLAUDE_API_KEY = "your-api-key-here"
```
4. Run the app: `streamlit run engineering.py`

Note: The vectorstore folder must be present in the same directory as engineering.py. It is included in this repository.

---

### API Key
The application requires a Claude API key from Anthropic. On Streamlit Cloud, this is stored in the app secrets under the key `CLAUDE_API_KEY`. For local use, store it in `.streamlit/secrets.toml` as shown above.

---

### Code Authorship
The following describes what was written by me, what was adapted, and what came from external sources.

**Written by me:**
- engineering.py - all code written by me, with CP2 additions (format_citations function, system prompt, metadata retrieval, citation display) developed in the Colab notebook and ported to the Streamlit app
- Engineering_AI_Chatbot_CP2.ipynb - all Colab notebook cells written by me
- evaluation_questions.csv - all 50 questions written by me
- requirements.txt - written by me with protobuf version pin added to fix deployment error

**Adapted from documentation and examples:**
- ChromaDB initialization and query pattern adapted from ChromaDB documentation (https://docs.trychroma.com)
- SentenceTransformer loading pattern adapted from sentence-transformers documentation (https://www.sbert.net)
- Anthropic API call structure adapted from Anthropic documentation (https://docs.anthropic.com)
- Streamlit session state pattern adapted from Streamlit documentation (https://docs.streamlit.io)

**External libraries used but no code copied:**
- All other library usage written from scratch based on documentation

---

### Checkpoint History
**Checkpoint 1 (CP1):**
- Basic RAG pipeline with 300-character chunks and 50-character overlap
- 124 total chunks
- Results: 35/40 fully answered (87.5%), 10/10 proper abstentions (100%), 0/40 hallucinations (0%)
- Five partial answers identified caused by policy sentences split at chunk boundaries

**Checkpoint 2 (CP2):**
- Added dedicated system prompt using Claude API system parameter
- Added format_citations() function to map answers to exact character positions in manual
- Added automated scorer (score_answer, run_evaluation) to eliminate manual review
- Added chunk parameter experiment loop testing four configurations (300/50, 400/75, 500/100, 600/150)
- Optimal configuration identified: Config B (400/75)
- Results: 38/40 fully answered (95.0%), 10/10 proper abstentions (100%), 0/200 hallucinations (0%)

---

### How to Update the System

**To update the Engineering Policy Manual:**
1. Replace the Engineering_Manual.docx file in the data folder on Google Drive
2. Run the Colab notebook from Cell 5 through Cell 8 to rebuild the vectorstore
3. Download the new vectorstore folder and replace the one in this repository
4. Push to GitHub and reboot the Streamlit app

**To adjust chunk parameters:**
- Chunk size and overlap are set in Cell 7 of the Colab notebook in the create_chunks() call
- Cell 17 of the notebook runs a systematic comparison across multiple configurations
- After running Cell 17, the vectorstore is automatically reset to Config B (400/75) at the end of the experiment loop. This ensures the vectorstore saved to Google Drive is always the optimal deployed configuration regardless of which configuration ran last during testing.
- After selecting new parameters, rebuild the vectorstore and update the repository

**To update the system prompt:**
- The system prompt is defined as SYSTEM_PROMPT in engineering.py
- Edit the rules directly in that variable and push to GitHub
- The same system prompt is also defined in Cell 10 of the Colab notebook and should be kept in sync

**To add evaluation questions:**
- Add rows to evaluation_questions.csv following the existing format
- Number, Category, Question, and Expected_Result columns are required
- Expected_Result must be either "Fully Answered" or "Proper Abstention"
- Rerun Cells 14-18 in the Colab notebook to score the updated question set
