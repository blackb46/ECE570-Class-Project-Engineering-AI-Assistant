
import streamlit as st
import anthropic
import chromadb
from sentence_transformers import SentenceTransformer

# Page Setup
st.title(" 👷‍♂️Municipal Engineering Chatbot")
st.write("Ask questions about the Engineering Policy Manual")

# Initialize models
if 'model' not in st.session_state:
    st.session_state.model = SentenceTransformer('all-MiniLM-L6-v2')
    st.session_state.db = chromadb.PersistentClient(path="vectorstore")
    st.session_state.collection = st.session_state.db.get_collection(name="manual_collection")

# User input
question = st.text_area("Ask a question about a policy for the City contained in the Engineering Policy Manual:", height=100)

# Search button
if st.button("Search"):
    if question:
        # Search the manual
        with st.spinner("Searching..."):
            # Search
            query_emb = st.session_state.model.encode(question).tolist()
            results = st.session_state.collection.query(
                query_embeddings=[query_emb], 
                n_results=3
            )

            # Build Context
            context = "\n\n".join([
                f"[SOURCE {i + 1}]
{chunk}" 
                for i, chunk in enumerate(results['documents'][0])
            ])

            # Get answer from Claude
            api_key = st.secrets["CLAUDE_API_KEY"]
            client = anthropic.Anthropic(api_key=api_key)

            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                messages=[{"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}]
            )

            # Display Answer
            st.subheader("Answer:")
            st.write(response.content[0].text)

            # Display Sources
            st.subheader("Sources:")
            for i, src in enumerate(results['documents'][0],1):
                with st.expander(f"Source {i}"):
                  st.text(src)
    else:
            st.warning("Please enter a question.")
