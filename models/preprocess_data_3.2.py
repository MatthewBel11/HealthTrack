import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Load data
data_path = os.path.join('MOCK_DATA_3.2.csv')
data = pd.read_csv(data_path)

# Print initial data and column names for debugging
print(data.head())
print("Column Names:", data.columns)

# Fill missing values with column means (numeric columns only)
numeric_columns = data.select_dtypes(include=[float, int]).columns
data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].mean())

# Define numerical features for scaling
numerical_features = [
    'Healthcare Access %', 'Income Level', 'Education Level %', 'Vaccination Rate %',
    'Antenatal Care %', 'Health Expenditure %', 'Urbanization Rate %',
    'Nutrition Level %', 'Sanitation Facilities %', 'Age of Mother',
    'Birth Rate %', 'Female Literacy Rate %'
]

# Scale numerical features
scaler = StandardScaler()
data[numerical_features] = scaler.fit_transform(data[numerical_features])

# Save preprocessed data
output_dir = os.path.join('..', 'pred_model')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'preprocessed_MOCK_DATA_3.2.csv')
data.to_csv(output_path, index=False)

# Save the scaler
scaler_path = os.path.join(output_dir, 'scaler_3.2.pkl')
joblib.dump(scaler, scaler_path)

print("Data preprocessing complete and saved to 'pred_model/preprocessed_MOCK_DATA_3.2.csv'")
