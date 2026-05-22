from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import numpy as np

from openai import OpenAI
from dotenv import load_dotenv

from rag import (
    create_vector_store,
    retrieve_relevant_data
)

import os


load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


datasets = {}

current_dataset = None

vector_stores = {}


@app.get("/")
def home():

    return {
        "message": "AI Data Analyst Backend Running 🚀"
    }


@app.post("/upload")
async def upload_csv(
    file: UploadFile = File(...)
):

    global datasets
    global current_dataset
    global vector_stores

    try:


        try:

            df = pd.read_csv(
                file.file,
                encoding="utf-8"
            )

        except:

            file.file.seek(0)

            try:

                df = pd.read_csv(
                    file.file,
                    encoding="latin1"
                )

            except:

                file.file.seek(0)

                df = pd.read_csv(
                    file.file,
                    encoding="cp1252"
                )


        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        df = df.drop_duplicates()

        df = df.replace(
            [np.inf, -np.inf],
            np.nan
        )

        numeric_cols = df.select_dtypes(
            include=np.number
        ).columns

        for col in numeric_cols:

            df[col] = df[col].fillna(
                df[col].mean()
            )

        categorical_cols = df.select_dtypes(
            include="object"
        ).columns

        for col in categorical_cols:

            df[col] = df[col].fillna(
                "Unknown"
            )

        dataset_name = file.filename

        datasets[dataset_name] = df

        current_dataset = dataset_name

    

        dataset_text = df.head(3000).to_string()

        vector_stores[dataset_name] = (
            create_vector_store(dataset_text)
        )

        return {

            "message":
            "Dataset uploaded successfully",

            "dataset":
            dataset_name,

            "rows":
            int(df.shape[0]),

            "columns":
            int(df.shape[1]),

            "available_datasets":
            list(datasets.keys())
        }

    except Exception as e:

        return {
            "error": str(e)
        }

@app.get("/switch-dataset")
def switch_dataset(
    dataset_name: str
):

    global current_dataset

    try:

        if dataset_name not in datasets:

            return {
                "error":
                "Dataset not found"
            }

        current_dataset = dataset_name

        return {
            "message":
            f"Switched to {dataset_name}"
        }

    except Exception as e:

        return {
            "error": str(e)
        }


@app.get("/datasets")
def get_datasets():

    global datasets
    global current_dataset

    return {

        "datasets":
        list(datasets.keys()),

        "current_dataset":
        current_dataset
    }


@app.get("/insights")
def get_insights():

    global datasets
    global current_dataset

    try:

        if current_dataset is None:

            return {
                "insights":
                "Upload dataset first"
            }

        df = datasets[current_dataset]

        rows = df.shape[0]

        columns = df.shape[1]

        numeric_cols = df.select_dtypes(
            include=np.number
        ).columns.tolist()

        categorical_cols = df.select_dtypes(
            include="object"
        ).columns.tolist()

        missing = int(
            df.isnull().sum().sum()
        )

        insights = f"""
📊 AI BUSINESS INSIGHTS

• Current Dataset:
{current_dataset}

• Dataset contains {rows} rows and {columns} columns.

• Missing values detected:
{missing}

• Numeric metrics available:
{", ".join(numeric_cols[:10])}

• Categorical dimensions available:
{", ".join(categorical_cols[:10])}

📈 Recommended Analysis

• Trend Analysis
• KPI Monitoring
• Comparative Analytics
• Business Intelligence
• Revenue Distribution
• Performance Monitoring

🔥 AI Observations

• Dataset appears structured for advanced analytics.
• Recommended visualizations include bar and line charts.
• KPI dashboard can effectively track performance.
• AI chatbot can answer business-related analytical queries.

🚀 Suggested Use Cases

• Executive dashboards
• Sales analysis
• Revenue monitoring
• Trend forecasting
• Product performance analysis
"""

        return {
            "insights": insights
        }

    except Exception as e:

        return {
            "insights": str(e)
        }


@app.get("/analytics")
def get_analytics():

    global datasets
    global current_dataset

    try:

        if current_dataset is None:

            return {
                "error":
                "Upload dataset first"
            }

        df = datasets[current_dataset]

        rows = int(df.shape[0])

        columns = int(df.shape[1])

        missing = int(
            df.isnull().sum().sum()
        )

        numeric_cols = df.select_dtypes(
            include=np.number
        ).columns.tolist()

        categorical_cols = df.select_dtypes(
            include="object"
        ).columns.tolist()

        highest_value = 0

        if len(numeric_cols) > 0:

            highest_value = round(
                float(
                    df[numeric_cols[0]].max()
                ),
                2
            )

        chart_data = {

            "labels": [],

            "values": []
        }

        if len(categorical_cols) > 0:

            best_col = categorical_cols[0]

            grouped = (
                df[best_col]
                .astype(str)
                .value_counts()
                .head(10)
            )

            chart_data = {

                "labels":
                grouped.index.tolist(),

                "values":
                grouped.values.tolist()
            }

        return {

            "rows": rows,

            "columns": columns,

            "missing": missing,

            "numeric_count":
            len(numeric_cols),

            "categorical_count":
            len(categorical_cols),

            "highest_value":
            highest_value,

            "chart_data":
            chart_data
        }

    except Exception as e:

        return {
            "error": str(e)
        }


@app.get("/columns")
def get_columns():

    global datasets
    global current_dataset

    try:

        if current_dataset is None:

            return {
                "error":
                "Upload dataset first"
            }

        df = datasets[current_dataset]

        numeric_cols = df.select_dtypes(
            include=np.number
        ).columns.tolist()

        categorical_cols = df.select_dtypes(
            include="object"
        ).columns.tolist()

        return {

            "numeric":
            numeric_cols,

            "categorical":
            categorical_cols
        }

    except Exception as e:

        return {
            "error": str(e)
        }

@app.get("/dynamic-chart")
def dynamic_chart(
    x_col: str,
    y_col: str,
    chart_type: str
):

    global datasets
    global current_dataset

    try:

        if current_dataset is None:

            return {
                "error":
                "Upload dataset first"
            }

        df = datasets[current_dataset]

        temp_df = df.copy()

        temp_df = temp_df.dropna(
            subset=[x_col]
        )

        if y_col == "count":

            grouped = (
                temp_df[x_col]
                .astype(str)
                .value_counts()
                .head(10)
            )

        else:

            grouped = (
                temp_df.groupby(x_col)[y_col]
                .mean()
                .sort_values(
                    ascending=False
                )
                .head(10)
            )

        labels = [
            str(x)
            for x in grouped.index.tolist()
        ]

        values = [
            round(float(v), 2)
            for v in grouped.values.tolist()
        ]

        return {

            "labels": labels,

            "values": values
        }

    except Exception as e:

        return {
            "error": str(e)
        }


@app.get("/ask")
def ask_ai(question: str):

    global datasets
    global current_dataset
    global vector_stores

    try:

        if current_dataset is None:

            return {
                "error":
                "Upload dataset first"
            }

        df = datasets[current_dataset]

        vector_store = vector_stores[
            current_dataset
        ]

        relevant_data = retrieve_relevant_data(
            vector_store,
            question
        )

        stats = df.describe(
            include="all"
        ).to_string()

        columns = list(df.columns)

        prompt = f"""
You are an advanced AI Data Analyst.

CURRENT DATASET:
{current_dataset}

DATASET COLUMNS:
{columns}

DATASET STATISTICS:
{stats}

RELEVANT DATA:
{relevant_data}

USER QUESTION:
{question}

RULES:

1. Answer professionally
2. Perform intelligent analysis
3. Give business insights
4. Use trends and comparisons
5. Use bullet points
6. Give calculations if required
7. Never dump raw CSV
8. Never say dataset unavailable
9. Explain trends if detected
10. Give actionable recommendations
11. Keep answers concise but insightful
"""

        completion = client.chat.completions.create(

            model="openai/gpt-3.5-turbo",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = (
            completion
            .choices[0]
            .message
            .content
        )

        return {

            "question": question,

            "answer": answer
        }

    except Exception as e:

        return {
            "error": str(e)
        }