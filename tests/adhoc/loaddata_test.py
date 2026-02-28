from rag_sql.db_init import create_db_from_csv
from rag_sql.langgraph_flow import ask_sql

create_db_from_csv("data/raw/Fraud Detection Dataset.csv")
state = ask_sql("What percentage of transactions are fraud?")
print(state)
