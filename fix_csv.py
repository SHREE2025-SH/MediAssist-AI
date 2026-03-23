import pandas as pd
import re

df = pd.read_csv(r'D:\Medassist AI\Medassist AI\dia_3.csv')

# Print column names so we know what to fix
print("Columns:", df.columns.tolist())
print("Before fix:")
print(df.iloc[:, 1].head(5))  # print first 5 disease names

# Clean ALL columns - remove invisible characters
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].apply(lambda x: re.sub(r'[^\x20-\x7E]', ' ', str(x)).strip() if pd.notna(x) else x)
        df[col] = df[col].str.replace(r'\s+', ' ', regex=True).str.strip()

print("\nAfter fix:")
print(df.iloc[:, 1].head(5))

df.to_csv(r'D:\Medassist AI\Medassist AI\dia_3.csv', index=False, encoding='utf-8')
print("\n✅ Done! dia_3.csv cleaned and saved.")

