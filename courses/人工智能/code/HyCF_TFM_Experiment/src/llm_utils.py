from openai import OpenAI
import time
import os

# Configuration from openai==1.40.py
API_KEY = "REDACTED_CONFIGURE_LOCALLY"
BASE_URL = "https://yunwu.ai/v1"

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

def get_embedding(text, model="text-embedding-3-small"):
    """
    Get embedding for a single text string.
    """
    text = text.replace("\n", " ")
    try:
        response = client.embeddings.create(
            model=model,
            input=[text]
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        # Return a zero vector of size 1536 (default for small in v3? or ada-002)
        # text-embedding-3-small default dim is 1536
        return [0.0] * 1536

def get_embeddings_batch(texts, model="text-embedding-3-small", batch_size=10):
    """
    Get embeddings for a list of texts.
    """
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        # Clean newlines
        batch = [t.replace("\n", " ") for t in batch]
        try:
            response = client.embeddings.create(
                model=model,
                input=batch
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
            time.sleep(0.5) # Rate limit protection
        except Exception as e:
            print(f"Error in batch embedding: {e}")
            all_embeddings.extend([[0.0]*1536 for _ in range(len(batch))])
            
    return all_embeddings

def generate_report(patient_data, prediction_prob):
    """
    Generate a clinical report using GPT-4o-mini.
    """
    
    prompt = f"""
    You are an expert cardiologist assistant. I will provide you with clinical data for a heart failure patient and a model's readmission risk prediction.
    
    Patient Data:
    - Clinical Note: {patient_data['text']}
    - Recent Lab Trends (Last 7 days): 
      BNP: {patient_data['latest_bnp']} (Trend: {patient_data['bnp_trend']})
      Creatinine: {patient_data['latest_creat']}
    
    Model Prediction:
    - 30-Day Readmission Probability: {prediction_prob:.2%}
    
    Please generate a concise 3-paragraph clinical report:
    1. Patient Summary: Summarize the key clinical features.
    2. Risk Analysis: Explain why the risk is high or low based on the text and lab trends.
    3. Recommendations: Suggest 2-3 specific interventions strictly based on the provided data.
    
    Output in Markdown format.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing report: {e}"
