import numpy as np
import pandas as pd
import os
import random

def generate_synthetic_data(num_samples=1000, output_dir='data'):
    """
    Generates synthetic data for HyCF-TFM experiment.
    
    Data modalities:
    1. Text (Discharge Summary): Simulated clinical text.
    2. Time-Series (Lab Events): 7 days of lab values (BNP, Creatinine, etc.).
    3. Image (CXR Features): Simulated pre-extracted ResNet features.
    4. Label: 30-day readmission (0/1).
    """
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Generating {num_samples} synthetic patient records...")
    
    data = []
    
    # Clinical text templates to make it look "almost real"
    templates = [
        "Patient admitted with symptoms of {symptoms}. Hx of {history}. Course: {course}. Discharge medications: {meds}. Follow-up in {followup} weeks.",
        "75yo male with {history}. Presented with {symptoms}. Treated with {meds}. Condition {status} upon discharge.",
        "{history} patient complaining of {symptoms}. Echo showed {echo}. Labs revealed {labs}. Discharged on {meds}.",
    ]
    
    symptoms_list = ["shortness of breath", "chest pain", "edema", "fatigue", "palpitations"]
    history_list = ["CHF", "HTN", "Diabetes", "AFib", "CAD"]
    meds_list = ["Lasix", "Lisinopril", "Carvedilol", "Metoprolol", "Furosemide"]
    status_list = ["improved", "stable", "guarded"]
    
    for i in range(num_samples):
        pid = f"P{str(i).zfill(5)}"
        
        # 1. Label Generation (based on some hidden logic to make it learnable)
        # Higher risk if older, certain keywords in text, or bad trends in labs
        risk_score = 0
        
        # 2. Time-Series Data Generation (7 days, 5 features)
        # Features: [BNP, Creatinine, Sodium, HR, SBP]
        # BNP trend is a strong predictor
        base_bnp = np.random.uniform(100, 800)
        base_creat = np.random.uniform(0.5, 2.0)
        
        # Simulate trends: Increasing BNP -> High Risk
        trend_type = np.random.choice(['stable', 'improving', 'worsening'], p=[0.5, 0.3, 0.2])
        
        ts_data = []
        for d in range(7):
            noise = np.random.normal(0, 10, 5) # random fluctuation
            
            if trend_type == 'worsening':
                bnp = base_bnp + (d * 50) + noise[0]
                creat = base_creat + (d * 0.1) + noise[1]/100
                risk_score += 0.1
            elif trend_type == 'improving':
                bnp = max(0, base_bnp - (d * 30) + noise[0])
                creat = max(0.5, base_creat - (d * 0.05) + noise[1]/100)
                risk_score -= 0.05
            else: # stable
                bnp = base_bnp + noise[0]
                creat = base_creat + noise[1]/100
            
            hr = np.random.normal(80, 10)
            sbp = np.random.normal(120, 15)
            sodium = np.random.normal(140, 3)
            
            ts_data.append([bnp, creat, sodium, hr, sbp])
            
        ts_data = np.array(ts_data) # Shape (7, 5)
        
        # Save Time-series to file (or keep in memory dataframe for simplicity, let's use a big CSV)
        # We will flatten it or store ID reference. For this script, let's store all in a dictionary or separate files.
        # To make it "almost real", let's save individual CSVs for time series or one big CSV.
        # Let's save one big CSV for time series with (PatientID, Day, Feature1...Feature5)
        
        # 3. Text Generation
        symptom = np.random.choice(symptoms_list)
        hist = np.random.choice(history_list)
        med = np.random.choice(meds_list)
        
        text = np.random.choice(templates).format(
            symptoms=symptom, history=hist, course="diuresis started", 
            meds=med, followup="2", status=np.random.choice(status_list),
            echo="EF 35%", labs="elevated BNP"
        )
        
        # Logic: "worsening" trend usually has "guarded" status or more severe text
        if trend_type == 'worsening':
            text += " Patient advised to return ED if symptoms worsen."
            risk_score += 0.5
        
        # 4. Image Features (Simulated ResNet-50 features: 2048-d)
        # If high risk, add some "signal" to the noise
        img_feats = np.random.normal(0, 1, 2048)
        if risk_score > 0.5:
            img_feats[:10] += 2.0 # Artificial signal in first 10 dims
        
        # Finalize Label
        # Add random noise to risk
        prob = 1 / (1 + np.exp(-(risk_score - 0.5))) # Sigmoid
        label = 1 if np.random.random() < prob else 0
        
        # Collect
        data.append({
            'patient_id': pid,
            'text': text,
            'label': label,
            'ts_data': ts_data.tolist(), # Store as list for JSON serialization or processing
            'img_path': f"images/{pid}.npy" # Pointer to simulated image feature file
        })
        
        # Save image features
        img_dir = os.path.join(output_dir, 'images')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        np.save(os.path.join(img_dir, f"{pid}.npy"), img_feats)

    # Save metadata/main dataframe
    df = pd.DataFrame(data)
    # Separate TS data to another file for realism (normalized relational DB style)
    
    # Save Main Clinical Data
    df[['patient_id', 'text', 'label', 'img_path']].to_csv(os.path.join(output_dir, 'clinical_data.csv'), index=False)
    
    # Save Time Series in Long Format
    ts_records = []
    for idx, row in df.iterrows():
        pid = row['patient_id']
        ts = np.array(row['ts_data'])
        for day in range(7):
            ts_records.append({
                'patient_id': pid,
                'day': day + 1,
                'BNP': ts[day, 0],
                'Creatinine': ts[day, 1],
                'Sodium': ts[day, 2],
                'HR': ts[day, 3],
                'SBP': ts[day, 4]
            })
    pd.DataFrame(ts_records).to_csv(os.path.join(output_dir, 'lab_vitals_ts.csv'), index=False)
    
    print(f"Data generation complete. Files saved in {output_dir}")
    print(f"- clinical_data.csv")
    print(f"- lab_vitals_ts.csv")
    print(f"- images/ (numpy feature files)")

if __name__ == "__main__":
    generate_synthetic_data()
