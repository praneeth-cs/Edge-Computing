# Sensor Data Simulator and Predictor

## Description

A Streamlit application that generates synthetic sensor data, manages a centralized sensor dataset, removes duplicate records, and trains machine learning models to predict sensor values and compare model performance.

## Features

### Sensor Data Simulation
Generates 24 hours of synthetic sensor readings for multiple sensors with configurable sampling frequencies and realistic value fluctuations.

### Dataset Management
- Upload generated CSV files
- Append records to a master dataset
- Automatically remove duplicate records
- Track duplicate-removal statistics
- Reset stored data and metadata

### Machine Learning Prediction
Trains and compares multiple regression models:

- Linear Regression
- Random Forest Regressor
- Gradient Boosting Regressor
- XGBoost (optional)

### Model Evaluation
Evaluates each model using R² score and identifies the best-performing model based on prediction accuracy.

## Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- XGBoost (optional)

## Installation

```bash
pip install streamlit pandas numpy scikit-learn xgboost
```

## Run

```bash
streamlit run app.py
```

## Project Workflow

1. Generate synthetic sensor data
2. Export data as CSV
3. Upload CSV files to the master dataset
4. Remove duplicate records automatically
5. Train machine learning models
6. Compare model performance
7. Identify the best prediction model

## Files

```text
app.py
master_sensor_data.csv
master_stats.json
README.md
```

## Future Enhancements

- Real-time sensor simulation
- Anomaly detection
- Forecasting future sensor values
- Database integration
- Interactive dashboards
- Hyperparameter optimization

## License

Add a license before publishing the repository.
