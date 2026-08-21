from extract import extract
from transform import transform
from load import load
 
def run_pipeline():
    raw = extract()
    clean = transform(raw)
    load(clean)
    print(f"Loaded {len(clean)} rows into crypto.db")
 
if __name__ == "__main__":
    run_pipeline()