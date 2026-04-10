
import streamlit as st
import anthropic
import chromadb
from sentence_transformers import SentenceTransformer

def format_citations(chunks, metadatas):
    # Takes the retrieved chunks and their metadata and formats them into 
    # verifiable citations that point back to the exact positions in the manual.
    # This was added during Checkpoint 2 so every answer could be verified 
    # against the source document.
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
SYSTEM_PROMPT = '''You are a municipal engineering policy assistant for a City

RULES YOU MUST FOLLOW:
1. Answer ONLY using the manual context provided. Never use outside knowledge.
2. Every factual claim must be supported by a retrieved source.
3. Do not embed source labels inside sentences. Instead, list all sources used on a separate line at the end of your answer, formatted as: *Sources used: [SOURCE 1], [SOURCE 2]*
4. If the answer requires combining information from multiple sources, list all of them.
5. If the manual context does not contain enough information to answer the question, respond with: "The Engineering Policy Manual does not contain specific information about [topic]. Please refer to the appropriate section or department for this information."
6. Never guess, infer, or fabricate policy requirements.
7. Be precise - include specific numbers, measurements and code references when present in the manual.'''

# Page Setup
st.title(" 👷‍♂️Municipal Engineering Chatbot")

# Initialize models
if 'model' not in st.session_state:
    st.session_state.model = SentenceTransformer('all-MiniLM-L6-v2')
    st.session_state.db = chromadb.PersistentClient(path="vectorstore")
    st.session_state.collection = st.session_state.db.get_collection(name="manual_collection")

# User input
st.subheader("Ask a question about a policy for the City contained in the Engineering Policy Manual:")
question = st.text_area("", height=100)

# Example questions shown below the input box
st.markdown("**Example questions you can ask:**")
st.markdown("""
- What is the minimum pipe diameter allowed for storm drain pipes?
- What is the maximum side slope allowed for a detention pond?
- What pipe material is required for storm drains under residential driveways?
- What is the minimum thickness of stone required for a stabilized construction exit?
- What is the average and minimum buffer width for a construction site adjacent to Exceptional Waters?
- What design storm frequency is required for local residential streets?
""")

# Search button
if st.button("Search"):
    if question:
        # Search the manual
        with st.spinner("Searching..."):
            # Search
            query_emb = st.session_state.model.encode(question).tolist()
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

            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}]
            )

            # Display Answer
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
