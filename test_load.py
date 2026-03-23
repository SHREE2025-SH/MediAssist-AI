import pandas as pd
from pathlib import Path

base_path = Path(".")

# Test loading all data
try:
    diseases = pd.read_csv(base_path / 'dia_3.csv')
    symptoms = pd.read_csv(base_path / 'symptoms2.csv')
    matrix = pd.read_csv(base_path / 'sym_dis_matrix.csv', index_col=0)
    medicines = pd.read_csv(base_path / 'medicines.csv')
    
    print("✓ All files loaded successfully")
    print(f"  Diseases: {diseases.shape}")
    print(f"  Symptoms: {symptoms.shape}")
    print(f"  Matrix: {matrix.shape}")
    print(f"  Medicines: {medicines.shape}")
    
    # Test column names
    print(f"\nDiseases columns: {diseases.columns.tolist()}")
    print(f"Symptoms columns: {symptoms.columns.tolist()}")
    print(f"Matrix index dtype: {matrix.index.dtype}")
    
    # Test the actual load_data function logic
    disease_id_col = '_id' if '_id' in diseases.columns else 'id'
    symptom_id_col = '_id' if '_id' in symptoms.columns else 'id'
    
    print(f"\nUsing columns: disease_id={disease_id_col}, symptom_id={symptom_id_col}")
    
    # Process like the app does
    diseases[disease_id_col] = pd.to_numeric(diseases[disease_id_col], errors='coerce')
    diseases = diseases.dropna(subset=[disease_id_col]).copy()
    diseases[disease_id_col] = diseases[disease_id_col].astype(int)
    diseases.set_index(disease_id_col, inplace=True)
    
    print(f"✓ Diseases processed, final shape: {diseases.shape}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
