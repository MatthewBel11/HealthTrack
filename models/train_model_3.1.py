import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import joblib
import os

# Load preprocessed data
data_path = os.path.join('..', 'pred_model', 'preprocessed_MOCK_DATA.csv')
data = pd.read_csv(data_path)

# Define features and target
features = [
    'Skilled Birth Attendants', 'Healthcare Access', 'Income Level', 'Education Level %',
    'Maternal Health Services %', 'Contraceptive Prevalence %', 'Antenatal Care %',
    'Health Expenditure %', 'Urbanization Rate %', 'Nutrition Level %',
    'Sanitation Facilities %', 'Age of Mother', 'Birth Rate %', 'Female Literacy Rate %'
]
target = 'Maternal Mortality Rate '

X = data[features]
y = data[target]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
rmse = mean_squared_error(y_test, y_pred, squared=False)
print(f'RMSE: {rmse}')

# Save the model
model_dir = os.path.join('..', 'models')
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, 'maternal_mortality_model.pkl')
joblib.dump(model, model_path)
print(f"Model training complete and saved to '{model_path}'")
