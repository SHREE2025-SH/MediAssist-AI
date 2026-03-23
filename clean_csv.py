import pandas as pd
import unicodedata
from pathlib import Path

def remove_invisible_chars(text):
    """Remove invisible unicode characters from text."""
    if not isinstance(text, str):
        return text
    
    # Remove control characters and invisible characters
    cleaned = ""
    for char in text:
        # Get the unicode category
        category = unicodedata.category(char)
        # Keep only visible characters (not in Cc, Cf, Cs, Co, Cn categories)
        # Cc = Control, Cf = Format, Cs = Surrogate, Co = Private Use, Cn = Not assigned
        if category not in ('Cc', 'Cf', 'Cs', 'Co', 'Cn'):
            cleaned += char
    
    return cleaned

def clean_csv_file(input_file):
    """Clean CSV file by removing invisible unicode characters."""
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    
    print(f"Original shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Apply cleaning to all string columns
    for col in df.columns:
        if df[col].dtype == 'object':  # String columns
            print(f"Cleaning column: {col}")
            df[col] = df[col].apply(remove_invisible_chars)
    
    # Also clean column names
    df.columns = [remove_invisible_chars(str(col)) for col in df.columns]
    
    print(f"Cleaned shape: {df.shape}")
    
    # Save with utf-8 encoding
    print(f"Saving cleaned file to {input_file}...")
    df.to_csv(input_file, index=False, encoding='utf-8')
    
    print("✅ File cleaned and saved successfully!")
    
    # Display first row to verify
    print("\nFirst row of cleaned data:")
    print(df.iloc[0])

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent
    csv_file = base_path / 'dia_3.csv'
    
    if csv_file.exists():
        clean_csv_file(csv_file)
    else:
        print(f"Error: {csv_file} not found!")
