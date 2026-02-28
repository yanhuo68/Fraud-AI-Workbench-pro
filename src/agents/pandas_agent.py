
import pandas as pd
from agents.llm_router import init_llm

def query_dataframe(df, user_query):
    """
    Generates and executes Pandas code based on a user query.
    Returns: The result of the execution (DataFrame, Series, value, or error message).
    """
    if df is None:
        return "No dataframe loaded."

    # 1. Prepare Schema Context
    # Limit to first 3 rows to avoid token overflow but give example values
    head_csv = df.head(3).to_csv(index=False)
    dtypes_str = df.dtypes.to_string()
    
    prompt = (
        "You are a Pandas Data Analysis Agent. Write a Python snippet to answer the user's question about the dataframe `df`.\n"
        f"Dataframe Schema (dtypes):\n{dtypes_str}\n\n"
        f"Data Sample (first 3 rows):\n{head_csv}\n\n"
        f"User Question: {user_query}\n\n"
        "Rules:\n"
        "1. WRITE ONLY CODE. No markdown, no comments, no 'python' prefix.\n"
        "2. Assume the dataframe is named `df`.\n"
        "3. The final result MUST be assigned to a variable named `result`.\n"
        "4. Do not use print().\n"
        "5. If the query asks for a plot, just prepare data. Plotting is not supported here yet.\n"
        "6. Handle date columns carefully. They might be strings. Use `pd.to_datetime` if needed.\n"
        "Example:\n"
        "result = df[df['amount'] > 5000]\n"
    )

    try:
        llm = init_llm("openai:gpt-4o-mini")
        response = llm.invoke(prompt)
        
        # Clean response
        code = response.content.replace("```python", "").replace("```", "").strip()
        
        # 2. Execute Code
        # Define local scope for execution
        local_scope = {"df": df, "pd": pd}
        
        # We wrap in generic try/exec
        exec(code, {}, local_scope)
        
        if "result" in local_scope:
            return local_scope["result"]
        else:
            return "Error: The generated code did not assign a 'result' variable."
            return "Error: The generated code did not assign a 'result' variable."
            
    except Exception as e:
        return f"Analysis Failed: {e}. Code generated was:\n{code if 'code' in locals() else 'None'}"

def generate_suggested_questions(df):
    """
    Generates 5 sample questions based on the dataframe schema.
    """
    if df is None: return []
    
    dtypes_str = df.dtypes.to_string()
    
    prompt = (
        "You are a Data Analyst. Based exclusively on the following dataframe schema, suggest 5 interesting questions a user might ask.\n"
        f"Schema:\n{dtypes_str}\n\n"
        "Rules:\n"
        "1. Return ONLY the questions, one per line.\n"
        "2. Keep them short and concise (under 10 words).\n"
        "3. Focus on aggregations, filters, and top/bottom lists.\n"
        "4. CRITICAL: Frame your questions using ONLY the columns provided in the schema. Do not guess or invent columns.\n"
        "5. Do not number the lines.\n"
    )
    
    try:
        llm = init_llm("openai:gpt-4o-mini")
        response = llm.invoke(prompt)
        questions = [q.strip() for q in response.content.split('\n') if q.strip()]
        return questions[:5]
    except:
        return [
            "Show me the first 5 rows",
            "Count records by category",
            "Show average values",
            "Find common outliers",
            "Filter for specific date"
        ]
