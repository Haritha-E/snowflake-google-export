import snowflake.connector
import pandas as pd
import datetime
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ---------------- Snowflake ----------------

conn = snowflake.connector.connect(
    user=os.environ['SNOWFLAKE_USER'],
    password=os.environ['SNOWFLAKE_PASSWORD'],
    account=os.environ['SNOWFLAKE_ACCOUNT'],
    warehouse='COMPUTE_WH',
    database='EXPORT_SALES_DB',
    schema='EXPORT_SCHEMA'
)

df = pd.read_sql("SELECT * FROM sales_data", conn)
conn.close()

file_name = f"sales_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
df.to_excel(file_name, index=False)

# ---------------- Google OAuth ----------------

creds = Credentials(
    None,
    refresh_token=os.environ['GOOGLE_REFRESH_TOKEN'],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ['GOOGLE_CLIENT_ID'],
    client_secret=os.environ['GOOGLE_CLIENT_SECRET']
)

service = build('drive', 'v3', credentials=creds)

folder_id = os.environ['DRIVE_FOLDER_ID']

file_metadata = {
    'name': file_name,
    'parents': [folder_id]
}

media = MediaFileUpload(
    file_name,
    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()

print("Upload successful. File ID:", file.get('id'))
