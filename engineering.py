"""
Municipal Engineering AI Chatbot — ECE 570 Final Project, Track 2 (Product/Prototype).

A Retrieval-Augmented Generation (RAG) chatbot that answers municipal engineering
policy questions grounded strictly in the City of Brentwood Engineering Policy Manual.

Architecture:
    Corpus      : Engineering_Manual.docx (30,775 characters, single source)
    Chunking    : Character-based, Configuration B (chunk_size=400, overlap=75, 95 chunks)
    Embeddings  : sentence-transformers all-MiniLM-L6-v2 (384-dim)
    Vector DB   : ChromaDB persistent collection (top-3 cosine retrieval)
    LLM         : Anthropic Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
    Grounding   : System prompt enforces source-only answers and explicit abstention
    UI          : Streamlit single-page app with expandable source citations

Reproducibility: see README.md for clone-and-run instructions.
Evaluation: 95.0% retrieval accuracy, 100% abstention accuracy, 0% hallucinations
on the 50-question evaluation bank (Configuration B).

Author: Kevin L. Blackburn, P.E., GISP — Purdue MSAI, Spring 2026
"""

import streamlit as st
import anthropic
import chromadb
from sentence_transformers import SentenceTransformer

def format_citations(chunks, metadatas):
    """Format retrieved ChromaDB chunks into verifiable source citations.

    Each citation maps a chunk back to its exact character-range location in the
    30,775-character Engineering Policy Manual, supporting independent verification
    of every answer against the source document. Added during Checkpoint 2 to
    satisfy the project requirements for grounding.

    Args:
        chunks (list[str]): The retrieved chunk texts from ChromaDB.
        metadatas (list[dict]): The corresponding metadata dicts (must contain
            'position' and may contain 'chunk_id').

    Returns:
        list[dict]: One citation dict per chunk, with keys: source_num, chunk_id,
            char_start, char_end, section_estimate, preview.
    """
    
    citations = []

    # Loop through each chunk and its matching metadata at the same time.
    for i, (chunk_text, meta) in enumerate(zip(chunks, metadatas)):

        # Get the character position where this chunk starts in the manual.
        position = meta.get('position', 0)

        # Calculate where the chunk ends by adding the length to the start position.
        char_end = position + len(chunk_text)

        # Estimate which part of the manual the chunk comes from
        # The manual is 30,775 characters by my count so I divided it into thirds
        if position < 10258:
            section_estimate = "Early sections (Setup, Drainage Standards)"
        elif position < 20516:
            section_estimate = "Middle sections (Construction, Buffers)"
        else:
            section_estimate = "Later sections (Permitting, SCM, Zoning)"

        citation = {
            'source_num': i + 1,
            'chunk_id': meta.get('chunk_id', f'chunk_{position}'),
            'char_start': position,
            'char_end': char_end,
            'section_estimate': section_estimate,
            'preview': chunk_text[:80].replace('\n', '') + '...'
        }
        citations.append(citation)
    return citations

# System prompt that tells the LLM how to behave when answering questions
# Kept as a separate variable so it is easy to find and update if needed
SYSTEM_PROMPT = '''You are a municipal engineering policy assistant for the City of Brentwood, Tennessee, 
that answers questions about the Brentwood Engineering Policy Manual using only the retrieved manual passages provided as [SOURCE 1], [SOURCE 2], and [SOURCE 3] in the user message.

RULES YOU MUST FOLLOW:
1. Answer ONLY using the manual context provided. Never use outside knowledge.
2. Every factual claim must be supported by a retrieved source.
3. Do not embed source labels inside sentences. Instead, list all sources used on a separate line at the end of your answer, formatted as: *Sources used: [SOURCE 1], [SOURCE 2]*
4. If the answer requires combining information from multiple sources, list all of them.
5. If the manual context does not contain enough information to answer the question, respond with: "The Engineering Policy Manual does not contain specific information about [topic]. Please refer to the appropriate section or department for this information."
6. Never guess, infer, or fabricate policy requirements.
7. Be precise - include specific numbers, measurements and code references when present in the manual.'''

# Page Setup
st.title("👷‍♂️Municipal Engineering Chatbot")

# Initialize models
if 'model' not in st.session_state:
    st.session_state.model = SentenceTransformer('all-MiniLM-L6-v2')
    st.session_state.db = chromadb.PersistentClient(path="vectorstore")
    st.session_state.collection = st.session_state.db.get_collection(name="manual_collection")

# User input
st.subheader("Ask a question about a policy for the City contained in the Engineering Policy Manual:")
with st.form(key="search_form"):
    question = st.text_area("", height=100)
    submitted = st.form_submit_button("Search")

# Search button
answer_placeholder = st.empty()
if submitted:
    if question:
        # Search the manual
        with st.spinner("Searching..."):
            # Search
            query_emb = st.session_state.model.encode(question).tolist()
            # Retrieve top-3 most similar chunks; matches the n_results value reported in the paper.
            results = st.session_state.collection.query(
                query_embeddings=[query_emb], 
                n_results=3,
                include=['documents', 'metadatas']
            )

            # Pull out chunks and metadata separately to build citations.
            chunks = results['documents'][0]
            metadatas=results['metadatas'][0]

            # Build Context
            context_parts = []
            for i, chunk in enumerate(chunks):
                context_parts.append("[SOURCE " + str(i + 1) + "]" + chr(10) + chunk)
            context = (chr(10) + chr(10)).join(context_parts)

            # Get answer from Claude
            api_key = st.secrets["CLAUDE_API_KEY"]
            client = anthropic.Anthropic(api_key=api_key)

            # System prompt is passed via the dedicated `system=` parameter (not embedded in
            # the user message) — this is what enforces the zero-hallucination grounding behavior.
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}]
            )

            # Display Answer
            with answer_placeholder.container():
                st.subheader("Answer:")
                st.write(response.content[0].text)

            # Display Sources
            citations = format_citations(chunks, metadatas)

            st.subheader("Sources:")
            for c in citations:
                with st.expander(f"Source {c['source_num']} - {c['section_estimate']}"):
                    st.write(f"**Location:** Characters {c['char_start']:,} - {c['char_end']:,} of 30,775")
                    st.write(f"**Chunk ID:** {c['chunk_id']}")
                    st.write(f"**Preview:** {c['preview']}")
                    st.text(chunks[c['source_num'] - 1])
    else:
        st.warning("Please enter a question.")

# Example questions shown below the input box
with st.expander("Example questions you can ask"):
    st.markdown("""
- What is the minimum pipe diameter allowed for storm drain pipes?
- What is the maximum side slope allowed for a detention pond?
- What pipe material is required for storm drains under residential driveways?
- What is the minimum thickness of stone required for a stabilized construction exit?
- What is the average and minimum buffer width for a construction site adjacent to Exceptional Waters?
- What design storm frequency is required for local residential streets?
""")
