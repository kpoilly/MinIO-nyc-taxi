# NYC Taxi Fare Prediction with MinIO
This repository contains a Machine Learning pipeline for predicting taxi fare prices in New York City using the NYC Taxi Dataset. The project focuses on integrating MinIO for object storage management using Boto3. Additionally, it employs MLflow for experiment tracking.

📌 Project Overview
The pipeline includes the following key components:

* Data Ingestion: A script to fetch and preprocess the last two months of NYC taxi data from their official website.
* Feature Engineering: A module to transform and prepare the dataset for model training.
* Model Training: A script that trains a Random Forest Regressor to predict taxi fares. The model experiments and metrics are logged with MLflow.

The project uses Docker Compose to deploy both MinIO and MLflow instances. The MinIO setup provides a scalable object storage solution, while MLflow ensures experiment reproducibility.


After completion of this use case, the tree structure of the project will be the following:
```bash
├───data
│   ├───processed
│   │   ├───X_test.csv
│   │   ├───X_train.csv
│   │   ├───y_test.csv
│   │   ├───y_train.csv
│   │   └───yellow_tripdata_sampled_features.csv
│   └───raw
│       ├───yellow_tripdata_YYYY-MM.parquet
│       ├───yellow_tripdata_YYYY-MM.parquet
│       └───yellow_tripdata_sampled.csv
├───docker
│   ├───Dockerfile.minio
│   └───Dockerfile.mlflow
├───models
│   └───model.pkl
├───src
│   ├───config
│   │   ├───config.py
│   │   └───minio_setup.py
│   ├───data
│   │   ├───__init__.py
│   │   └───data_ingestion.py
│   ├───features
│   │   ├───__init__.py
│   │   └───build_features.py
│   ├───models
│   │   ├───__init__.py
│   │   └───train_model.py
│   └───__pycache__
├───.env
├───.gitignore
├───docker-compose.yml
├───LICENCE
├───README.md
└───requirements.txt
```

During this use case we'll mainly focus on the completion of the src scripts as to put in place Minio as the object storage solution. Let's get started!

## 🚀 First Steps
Before diving into the project, follow these initial setup steps:

1. Fork & Clone the Repository
To get started, fork this repository to your GitHub account. Then, clone it to your local machine using:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/NYC-Taxi-Fare-Prediction-MinIO.git
cd NYC-Taxi-Fare-Prediction-MinIO
```

2. Create & Activate a Virtual Environment
It’s recommended to use a virtual environment to manage dependencies. Run the following:
For Windows (PowerShell):

```bash
python -m venv venv
venv\Scripts\Activate
```

For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install Dependencies
With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

You're now ready to explore the project! 🚀
