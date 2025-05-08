def main(request):
    import json
    import pandas as pd
    from google.cloud import bigquery
    from cities_aqicn import get_air_quality_by_city
    from const import CITY
    from datetime import datetime  # Import datetime for the current timestamp

    # Replace with your JSON (or load it from a file or API response)
    json_data = get_air_quality_by_city(city=CITY)

    if not json_data:
        print("Failed to retrieve air quality data. Exiting.")
        exit(1)

    # Handle forecast daily: create a separate table
    def forecast_to_df(pollutant_type):
        forecast_list = json_data["forecast"]["daily"].get(pollutant_type, [])
        for f in forecast_list:
            f["type"] = pollutant_type
        return pd.DataFrame(forecast_list)

    forecast_pm10 = forecast_to_df("pm10")
    forecast_pm25 = forecast_to_df("pm25")
    forecast_uvi = forecast_to_df("uvi")

    df_forecast = pd.concat([forecast_pm10, forecast_pm25, forecast_uvi], ignore_index=True)

    # Ensure the 'day' column is of DATE type and other columns have correct types
    df_forecast['day'] = pd.to_datetime(df_forecast['day'], errors='coerce').dt.date  # Convert to DATE format
    df_forecast['avg'] = pd.to_numeric(df_forecast['avg'], errors='coerce', downcast='integer')  # Ensure INTEGER type
    df_forecast['min'] = pd.to_numeric(df_forecast['min'], errors='coerce', downcast='integer')  # Ensure INTEGER type
    df_forecast['max'] = pd.to_numeric(df_forecast['max'], errors='coerce', downcast='integer')  # Ensure INTEGER type
    df_forecast['type'] = df_forecast['type'].astype(str)  # Ensure STRING type

    # Add the current timestamp to the 'lastupdated' column
    df_forecast['lastupdated'] = datetime.now() # Use UTC timestamp

    # Check for invalid rows and drop them if necessary
    if df_forecast.isnull().any(axis=None):
        print("Warning: Some rows in df_forecast contain invalid data and will be dropped.")
        df_forecast = df_forecast.dropna()

    # Define the schema for the air_quality_forecast table
    forecast_schema = [
        bigquery.SchemaField("day", "DATE", mode="NULLABLE"),
        bigquery.SchemaField("avg", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("min", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("max", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("lastupdated", "TIMESTAMP", mode="NULLABLE"),  # Add schema for 'lastupdated'
    ]

    # Initialize BigQuery client
    client = bigquery.Client(project="planar-lacing-453703-g5")

    # Define dataset and table names
    dataset_id = "dbt_ahoang"
    forecast_table_id = f"{dataset_id}.air_quality_forecast"

    # Upload forecast data with the defined schema
    job_config = bigquery.LoadJobConfig(schema=forecast_schema)
    job_forecast = client.load_table_from_dataframe(df_forecast, forecast_table_id, job_config=job_config)
    job_forecast.result()

    print("Upload complete.")

    return "Main upload completed."