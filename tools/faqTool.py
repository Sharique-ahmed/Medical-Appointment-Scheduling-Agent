from langchain.tools import StructuredTool
from utils import gptClient,index,EMBEDDING_MODEL


def get_context_from_pinecone(query: str):
    """
    Exactly as you wrote it: embed using your OpenAI client and query the Pinecone index.
    Returns list of dicts with question/answer/score.
    """
    # Embed the query first
    queryEmb = gptClient.embeddings.create(model=EMBEDDING_MODEL, input=query).data[0].embedding

    # Get the top K values
    results = index.query(vector=queryEmb, top_k=3, include_metadata=True)

    # Append the result into the final list of dict
    docs = []
    for r in results.matches:
        docs.append({
            "question": r.metadata.get('question'),
            "answer": r.metadata.get('answer'),
            "score": f"{r.score:.3f}"
        })

    return docs


faq_tool = StructuredTool.from_function(
    name="faq_lookup",
    func=get_context_from_pinecone,
    description="Search the clinic FAQ vector database and return relevant Q&A pairs. Call with a single query string. Summarize the output and generate a response on your own, Don't Copy paste the output"
)