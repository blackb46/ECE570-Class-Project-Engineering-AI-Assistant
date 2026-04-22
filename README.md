# Municipal Engineering AI Chatbot
## ECE 570 Course Project - Track 2 Product Prototype

### Project Overview
My project is a Retrieval-Augmented Generation (RAG) system that answers municipal engineering policy questions using only the content of the official Engineering Policy Manual. This is intended to provide complete control over the corpus document provided. The system is designed to provide accurate, citation-grounded answers while properly refusing to answer questions that fall outside the content of the manual.

The system is deployed as a web application using Streamlit and uses ChromaDB for vector storage, the all-MiniLM-L6-v2 sentence transformer for embeddings, and the Claude API for answer generation.

------

### Live Deployment
The application is currently deployed and accessible at the following Streamlit link:

https://ece570-class-project-engineering-ai-assistant-gvtxjsbgzc6pkujc.streamlit.app/

-----

### Reproducibility Quickstart
For graders who want to run this locally in under two minutes:
1. `git clone https://github.com/blackb46/ece570-class-project-engineering-ai-assistant.git`
2. `cd ece570-class-project-engineering-ai-assistant`
3. `pip install -r requirements.txt`
4. Create `.streamlit/secrets.toml` with `CLAUDE_API_KEY = "your-anthropic-key"`
5. `streamlit run engineering.py`

The committed `vectorstore/` folder is pre-built using **Configuration B (chunk size 400, overlap 75, 95 chunks, 384-dim all-MiniLM-L6-v2 embeddings)** — no rebuild is required to run the app. To verify or rebuild from scratch, run the Colab notebook (`Engineering_AI_Chatbot_CP2.ipynb`) end-to-end; Cell 17 ends by resetting the vectorstore to Config B, ensuring the rebuilt index matches the deployed configuration.

**Source for evaluation results:** `Engineering_AI_Chatbot_CP2.ipynb`, Cell 17 — all numbers reported in the term paper trace back to this cell's executed output. Raw CSVs are in the Google Drive folder linked above.
-----

### Code and Materials
This project is split across two locations:

**GitHub Repository (Streamlit deployment code):**
https://github.com/blackb46/ece570-class-project-engineering-ai-assistant

Contains:
- `engineering.py` - the deployed Streamlit web application that was developed by the Colab notebook
- `requirements.txt` - Python dependencies for Streamlit Cloud
- `README.md` - this is this current file
- `vectorstore/` - pre-built ChromaDB index built by the Colab notebook Engineering Policy Manual (in .docx format) using Configuration B (400/75) where chunk size is 400 characters and overlap is 75 characters

**Google Drive (Colab development notebook and evaluation files):**
https://drive.google.com/drive/folders/1lIahiHz681nWmhUoXTqvCxo4174GzAIn?usp=sharing

Contains:
- `Engineering_AI_Chatbot_CP2.ipynb` - full development and evaluation notebook - this notebook sets everything up to then carry over to the GitHub repo
- `evaluation_questions.csv` - 50-question test bank used for evaluation based on common questions used in the Engineering Department
- `baseline_evaluation_results.csv` - baseline 50-question evaluation results - establishes baseline to measure from (originally the CP1 result file)
- `cp2_evaluation_results.csv` - CP2 four-configuration (multiple chunk sizes and overlap configurations) experiment results (200 scored answers)
- `data/Engineering_Manual.docx` - source policy manual used as the reference document
- `Checkpoint_01_Backup/` - CP1 code and results preserved for reference - just a backup showing previous runs and analysis prior to CP2

-----

### Repository Structure
```
engineering.py          # Main Streamlit web application - file is created in Colab and then manually copied into the GitHub repo
requirements.txt        # Python dependencies
README.md               # This file
vectorstore/            # ChromaDB persistent vector database folder
chroma.sqlite3          # Vector index built from the Engineering Policy Manual
```

-----

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

-----

### API Key
The application requires a Claude API key from Anthropic. On Streamlit Cloud, this is stored in the app secrets under the key `CLAUDE_API_KEY`. For local use, store it in `.streamlit/secrets.toml` as shown below.

-----

### How to Run Locally
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.streamlit/secrets.toml` file using your desired Claude API key discussed above:
```
CLAUDE_API_KEY = "your-api-key-here"
```
4. Run the app: `streamlit run engineering.py`

Note: The vectorstore folder must be present in the same directory as engineering.py. It is included in this GitHub repo.

-----

### Code Authorship
The following describes what was written personally by me, what was adapted, and what came from any external sources.

**Written by me:**
- engineering.py - all code written by me, with CP2 additions (format_citations function, system prompt, metadata retrieval, citation display) developed in the Colab notebook, copied to the GitHub repo, and ported to the Streamlit app
- Engineering_AI_Chatbot_CP2.ipynb - all Colab notebook cells written by me
- evaluation_questions.csv - all 50 questions written by me based on experience working in the Engineering Department at the City
- requirements.txt - written by me with protobuf version pin added to fix any deployment errors

**Adapted from documentation and examples:**
- ChromaDB initialization and query pattern adapted from ChromaDB documentation (https://docs.trychroma.com)
- SentenceTransformer loading pattern adapted from sentence-transformers documentation (https://www.sbert.net)
- Anthropic API call structure adapted from Anthropic documentation (https://docs.anthropic.com)
- Streamlit session state pattern adapted from Streamlit documentation (https://docs.streamlit.io)

**External libraries used but no code copied:**
- All other library usage written from scratch based on documentation

-----

### Checkpoint History
**Checkpoint 1 (CP1):**
- Basic RAG pipeline with 300-character chunks and 50-character overlap
- 124 total chunks
- Results: 35/40 fully answered (87.5%), 10/10 proper abstentions (100%), 0/40 hallucinations (0%)
- Five partial answers identified caused by policy sentences split at chunk boundaries

**Checkpoint 2 (CP2):**
- Added dedicated system prompt using Claude API system parameter
- Added `format_citations()` function to map answers to exact character positions in manual
- Added `automated scorer (score_answer, run_evaluation)` to eliminate continual manual review
- Added chunk parameter experiment loop testing four configurations (A: 300/50, B: 400/75, C: 500/100, and D: 600/150)
- Optimal configuration identified: Config B (400/75)
- Results: across four configurations (200 scored answers total): 0/200 hallucinations (0%) and 100% proper abstention in every configuration. Config B (400/75) was the best-performing chunk configuration at 38/40 fully answered (95.0%).

Note: Cell 17 of the notebook was re-executed after CP1 submission for Streamlit Cloud deployment preparation. The re-execution produced a baseline (CP1) score of 36/40 (90.0%) and a Config D score of 37/40 (92.5%). The report preserves the as-submitted CP1 values (35/40 = 87.5% and 35/40 = 87.5% respectively) for historical accuracy. Config B's 38/40 = 95.0% result is identical in both runs.

-----

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
- After selecting new parameters, rebuild the vectorstore and update the repository. This can be seen at the end of Cell 17 where you can actually select the proper config based on the results to properly build the vectorstore.

**To update the system prompt:**
- The system prompt is written to give the instructions and rules to the LLM on how to respond.
- The system prompt is defined as `SYSTEM_PROMPT` in `engineering.py`
- Edit the rules directly in that variable and manually overwrite the `engineering.py` file in the GitHub repo
- The same system prompt is also defined in Cell 10 of the Colab notebook and should be kept in sync across all notebooks and code.

**To add evaluation questions:**
- Add rows to `evaluation_questions.csv` following the existing format
- Number, Category, Question, and Expected_Result columns are required
- Expected_Result must be either "Fully Answered" or "Proper Abstention"
- Rerun Cells 14-18 in the Colab notebook to score the updated question set
