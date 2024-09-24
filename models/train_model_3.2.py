import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import joblib
import os

# Load preprocessed data
data_path = os.path.join('..', 'pred_model', 'preprocessed_MOCK_DATA_3.2.csv')
data = pd.read_csv(data_path)

# Define features and target variable
features = [
    'Healthcare Access %', 'Income Level', 'Education Level %', 'Vaccination Rate %',
    'Antenatal Care %', 'Health Expenditure %', 'Urbanization Rate %',
    'Nutrition Level %', 'Sanitation Facilities %', 'Age of Mother',
    'Birth Rate %', 'Female Literacy Rate %'
]
target = 'Infant Mortality Rate %'

X = data[features]
y = data[target]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate the model
predictions = model.predict(X_test)
rmse = mean_squared_error(y_test, predictions, squared=False)
print(f'RMSE: {rmse}')

# Save the trained model
output_dir = os.path.join('..', 'models')
os.makedirs(output_dir, exist_ok=True)
model_path = os.path.join(output_dir, 'infant_mortality_model.pkl')
joblib.dump(model, model_path)
print(f'Model training complete and saved to {model_path}')
