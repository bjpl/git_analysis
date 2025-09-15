# Data & Analytics File Types Guide

## Overview
Data processing and analytics tools enable organizations to extract insights, build predictive models, and create compelling visualizations. This guide covers essential file types for data workflows.

## File Types Reference

| **Tool Type** | **Core Files** | **Supporting Files** | **Purpose** |
|--------------|----------------|---------------------|------------|
| **ETL Pipelines** | `.py`, `.sql` | `.json`, `.csv`, `.parquet` | Data transformation and migration |
| **Data Visualizations** | `.html`, `.js` | `.json`, `.csv`, `.svg` | Business intelligence dashboards |
| **Jupyter Notebooks** | `.ipynb` | `.py`, `.md`, `.html` | Interactive data analysis |
| **SQL Query Builders** | `.sql` | `.py`, `.js`, `.yaml` | Database queries and reports |
| **Data Processing** | `.py`, `.r`, `.julia` | `.scala`, `.m` | Statistical analysis and ML |

## Use Cases & Examples

### ETL Pipelines
**Best For:** Data warehousing, migration, real-time processing
```python
# etl_pipeline.py - Apache Airflow DAG
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def extract_data(**context):
    """Extract data from source"""
    df = pd.read_csv('source_data.csv')
    return df.to_json()

def transform_data(**context):
    """Transform and clean data"""
    data = context['task_instance'].xcom_pull(task_ids='extract')
    df = pd.read_json(data)
    df['processed_date'] = datetime.now()
    df = df.dropna()
    return df.to_json()

def load_data(**context):
    """Load data to warehouse"""
    data = context['task_instance'].xcom_pull(task_ids='transform')
    df = pd.read_json(data)
    df.to_sql('warehouse_table', connection, if_exists='append')

dag = DAG(
    'etl_pipeline',
    default_args={'retries': 2},
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1)
)

extract = PythonOperator(task_id='extract', python_callable=extract_data, dag=dag)
transform = PythonOperator(task_id='transform', python_callable=transform_data, dag=dag)
load = PythonOperator(task_id='load', python_callable=load_data, dag=dag)

extract >> transform >> load
```
**Example Projects:** Customer data pipelines, log processing, real-time analytics

### Data Visualizations
**Best For:** Dashboards, reports, interactive charts
```javascript
// dashboard.js - D3.js visualization
const margin = {top: 20, right: 30, bottom: 40, left: 50};
const width = 800 - margin.left - margin.right;
const height = 400 - margin.top - margin.bottom;

// Load and visualize data
d3.csv('sales_data.csv').then(data => {
  // Parse data
  data.forEach(d => {
    d.date = d3.timeParse('%Y-%m-%d')(d.date);
    d.value = +d.value;
  });

  // Create scales
  const x = d3.scaleTime()
    .domain(d3.extent(data, d => d.date))
    .range([0, width]);

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.value)])
    .range([height, 0]);

  // Create line
  const line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.value));

  // Render chart
  const svg = d3.select('#chart')
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom);

  svg.append('path')
    .datum(data)
    .attr('fill', 'none')
    .attr('stroke', 'steelblue')
    .attr('d', line);
});
```
**Example Projects:** Sales dashboards, performance metrics, geographic visualizations

### Jupyter Notebooks
**Best For:** Exploratory analysis, model development, research
```python
# analysis.ipynb cells
# Cell 1: Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Cell 2: Load and explore data
df = pd.read_csv('dataset.csv')
print(df.info())
print(df.describe())

# Cell 3: Visualize distributions
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
df.hist(axes=axes.flatten())
plt.tight_layout()

# Cell 4: Train model
X = df.drop('target', axis=1)
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
print(f"Accuracy: {model.score(X_test, y_test):.2f}")
```
**Example Projects:** Data exploration, model prototyping, statistical analysis

## Best Practices

1. **Data Validation:** Implement schema validation and data quality checks
2. **Version Control:** Track data transformations and model versions
3. **Documentation:** Document data sources, transformations, and assumptions
4. **Testing:** Unit test data pipelines and transformations
5. **Monitoring:** Track pipeline performance and data quality metrics
6. **Security:** Encrypt sensitive data and implement access controls

## File Organization Pattern
```
data-project/
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── notebooks/
│   ├── exploratory/
│   └── modeling/
├── src/
│   ├── pipelines/
│   ├── transformations/
│   └── visualizations/
├── sql/
│   ├── queries/
│   └── migrations/
├── tests/
└── reports/
```

## Data Formats

### Parquet Files
```python
# Efficient columnar storage
df.to_parquet('data.parquet', compression='snappy')
df = pd.read_parquet('data.parquet')
```

### SQL Query Patterns
```sql
-- Window functions for analytics
SELECT 
  date,
  sales,
  AVG(sales) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7d,
  RANK() OVER (PARTITION BY month ORDER BY sales DESC) as monthly_rank
FROM sales_data;
```

## Performance Considerations
- Columnar storage (Parquet, ORC) for analytics
- Partitioning for large datasets
- Indexing for query optimization
- Parallel processing with Dask or Spark
- Caching intermediate results
- Incremental processing for streaming data

## Tools & Frameworks
- **ETL:** Apache Airflow, Luigi, Prefect, dbt
- **Visualization:** D3.js, Plotly, Tableau, Power BI
- **Notebooks:** Jupyter, Google Colab, Databricks
- **Processing:** Pandas, Apache Spark, Dask
- **Databases:** PostgreSQL, ClickHouse, Snowflake