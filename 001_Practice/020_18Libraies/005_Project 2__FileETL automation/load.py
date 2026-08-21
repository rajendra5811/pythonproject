from sqlalchemy import create_engine
 
def load(df):
    """Write the cleaned rows into a local SQLite database."""
    engine = create_engine("sqlite:///crypto.db")
    df.to_sql("coins", engine, if_exists="replace", index=False)