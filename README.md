# NYC Taxi Fare Prediction with MinIO
This repository contains a Machine Learning pipeline for predicting taxi fare prices in New York City using the NYC Taxi Dataset. The project focuses on integrating MinIO for object storage management using Boto3. Additionally, it employs MLflow for experiment tracking.

📌 Project Overview
The pipeline includes the following key components:

* Data Ingestion: A script to fetch and preprocess the last two months of NYC taxi data from their official website.
* Feature Engineering: A module to transform and prepare the dataset for model training.
* Model Training: A script that trains a Random Forest Regressor to predict taxi fares. The model experiments and metrics are logged with MLflow.

The project uses Docker Compose to deploy both MinIO and MLflow instances. The MinIO setup provides a scalable object storage solution, while MLflow ensures experiment reproducibility.