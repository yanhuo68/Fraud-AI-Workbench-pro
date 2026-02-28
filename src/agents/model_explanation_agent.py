import pandas as pd
from agents.llm_router import init_llm

def explain_model_prediction(
    df_row: pd.Series,
    probability: float,
    model_name: str,
    llm_id: str = "openai:gpt-4o-mini",
    schema_text: str = ""
) -> str:
    """
    Generates an LLM-based explanation for a high-risk fraud prediction.
    
    Args:
        df_row (pd.Series): The data row being scored.
        probability (float): The fraud probability produced by the model.
        model_name (str): The name/type of the model used (e.g., 'RandomForestClassifier').
        llm_id (str): The ID of the LLM to use for generation.
        schema_text (str): Optional context about the dataset schema.
        
    Returns:
        str: A markdown explanation of why this transaction might be fraudulent.
    """
    
    llm = init_llm(llm_id)
    
    # Convert row to a readable string format
    row_str = df_row.to_markdown() if hasattr(df_row, 'to_markdown') else str(df_row)
    
    prompt = f"""
    You are an expert fraud analyst explainer.
    
    A Machine Learning model ({model_name}) has flagged the following transaction as High Risk with a probability of {probability:.2%}.
    
    Transaction Data:
    {row_str}
    
    Relevant Schema Context:
    {schema_text}
    
    Task:
    Explain WHY this transaction received such a high score.
    - Highlight suspicious feature values (e.g. extremely high amounts, strange locations, high frequency).
    - If the probability is low but you are asked to explain, explain why it appears normal.
    - Write in clear, concise professional language suitable for a risk dashboard.
    - Use bullet points for key risk factors.
    """
    
    response = llm.invoke(prompt)
    return response.content
