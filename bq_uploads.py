def main(request):
    import pandas as pd
    from google.cloud import bigquery
    from cities_aqicn import get_air_quality_by_station
    from datetime import datetime  # Import datetime for the current timestamp
    from const import STATIONS  # Import the list of stations from const.py

    # Fetch the JSON data
    json_data = get_air_quality_by_station(stations=STATIONS)

    if not json_data:
        print("Failed to retrieve air quality data. Exiting.")
        exit(1)

    # Initialize a list to store records
    records = []

    # Iterate over each station in the JSON data
    for station_id, station_data in json_data.items():
        # Skip entries with errors or invalid data
        if station_data.get("status") == "error":
            continue

        # Handle cases where 'aqi' is '-'
        aqi_value = station_data.get("aqi")
        if aqi_value == '-':
            aqi_value = None  # Convert '-' to None

        # Flatten top-level data for each station
        record = {
            "station_id": station_id,
            "aqi": aqi_value,
            "idx": station_data.get("idx"),
            "dominentpol": station_data.get("dominentpol"),
            "city_name": station_data["city"].get("name"),
            "city_url": station_data["city"].get("url"),
            "city_lat": station_data["city"]["geo"][0],
            "city_lon": station_data["city"]["geo"][1],
            "time_s": station_data["time"].get("s"),
            "time_iso": station_data["time"].get("iso"),
            "debug_sync": station_data.get("debug", {}).get("sync"),
            "lastupdated": datetime.now(),  # Add the current UTC timestamp
        }

        # Add IAQI values
        for pollutant, val in station_data.get("iaqi", {}).items():
            record[f"iaqi_{pollutant}"] = val.get("v")

        # Append the record to the list
        records.append(record)

    # Convert the list of records to a DataFrame
    df_main = pd.DataFrame(records)

    # Define dataset and table names
    dataset_id = "dbt_ahoang"
    main_table_id = f"{dataset_id}.air_quality_main"

    # Define the schema for the air_quality_main table
    main_schema = [
        bigquery.SchemaField("station_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("aqi", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("idx", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("dominentpol", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("city_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("time_s", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("debug_sync", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("lastupdated", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("iaqi_co", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("iaqi_dew", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("iaqi_h", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("iaqi_no2", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("iaqi_p", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("iaqi_pm10", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("iaqi_pm25", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("iaqi_t", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("iaqi_w", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("iaqi_o3", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("iaqi_so2", "FLOAT", mode="NULLABLE"),
    ]

    # Initialize BigQuery client
    client = bigquery.Client(project="planar-lacing-453703-g5")

    # Upload main record with the defined schema
    job_config = bigquery.LoadJobConfig(schema=main_schema)
    job_main = client.load_table_from_dataframe(df_main, main_table_id, job_config=job_config)
    job_main.result()

    print("Main table upload complete.")
    return "Main upload completed."
