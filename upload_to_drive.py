import snowflake.connector
import pandas as pd
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json

# 1. Connect to Snowflake

conn = snowflake.connector.connect(
    user=os.environ['SNOWFLAKE_USER'],
    password=os.environ['SNOWFLAKE_PASSWORD'],
    account=os.environ['SNOWFLAKE_ACCOUNT'],
    warehouse='COMPUTE_WH',
    database='EXPORT_SALES_DB',
    schema='EXPORT_SCHEMA'
)

query = "SELECT * FROM sales_data"
df = pd.read_sql(query, conn)
conn.close()

# 2. Create Excel File

file_name = f"sales_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
df.to_excel(file_name, index=False)

# 3. Google Drive Authentication

SCOPES = ['https://www.googleapis.com/auth/drive']

service_account_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])

credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=SCOPES
)

drive_service = build('drive', 'v3', credentials=credentials)

# 4. Upload File to Drive Folder

folder_id = os.environ['DRIVE_FOLDER_ID']

file_metadata = {
    'name': file_name,
    'parents': [folder_id]
}

media = MediaFileUpload(
    file_name,
    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

file = drive_service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()

print("Upload successful. File ID:", file.get('id'))
