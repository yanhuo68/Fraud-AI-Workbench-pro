
from agents.llm_router import init_llm

def query_document(content, user_query):
    """
    Simulated RAG: Sends truncated content + question to LLM.
    Returns: Textual answer.
    """
    if not content:
        return "No content loaded."
        
    # Truncate content to avoid token overflow (simple approach)
    # Ideally should use vector store, but for "Chat with Data" feature on single file, this is fine
    truncated_content = content[:20000] 
    
    prompt = (
        "You are an expert Document Analyst. Answer the user's question based strictly on the document content below.\n"
        "If the answer is not in the text, say 'I cannot find that information in the document.'\n\n"
        f"Document Content (Truncated):\n{truncated_content}\n\n"
        f"User Question: {user_query}\n\n"
        "Answer:"
    )

    try:
        llm = init_llm("openai:gpt-4o-mini")
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Analysis Failed: {e}"

def generate_document_questions(content):
    """
    Generates 5 sample questions based on text content.
    """
    if not content: return []
    
    truncated_content = content[:5000]
    
    prompt = (
        "You are a Document Analyst. Skim the following text and suggest 5 interesting questions a user might ask.\n"
        f"Text:\n{truncated_content}\n\n"
        "Rules:\n"
        "1. Return ONLY the questions, one per line.\n"
        "2. Keep them short and concise (under 10 words).\n"
        "3. Focus on key themes, risks, and entities.\n"
        "4. Do not number the lines.\n"
    )
    
    try:
        llm = init_llm("openai:gpt-4o-mini")
        response = llm.invoke(prompt)
        questions = [q.strip() for q in response.content.split('\n') if q.strip()]
        return questions[:5]
    except:
        return [
            "Summarize the main points",
            "What are the key risks?",
            "Who are the people mentioned?",
            "What are the dates involved?",
            "Explain the technical terms"
        ]
