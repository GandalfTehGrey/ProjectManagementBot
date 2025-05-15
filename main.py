import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import requests
from datetime import datetime

# --- SETUP PATH ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = "credentials.json"  # ✅ Matches workflow location


# --- CONFIG ---
SPREADSHEET_NAME = 'Google Sheets Integraton Test'
SHEET_NAME = 'Sheet1'
WEBHOOK_URL = 'https://default07c37c88435f4587adb72b0b979470.e0.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/8c1bb488b6ce496b84a53165e84df6b2/triggers/manual/paths/invoke/?api-version=1&tenantId=tId&environmentName=Default-07c37c88-435f-4587-adb7-2b0b979470e0&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=qT7GoXBo46-zM0mW1Ek2fcFm50GCirDjKWPKWWo2WLw'

# --- AUTHENTICATE ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

# --- FETCH DATA ---
rows = sheet.get_all_values()
headers = rows[2]  # Row 3: Task headings
employees = rows[3:6]  # Row 4–6: Employee data

# --- DETERMINE TODAY'S COLUMN INDICES ---
day = datetime.now().strftime('%A')  # e.g., 'Monday'
day_to_col = {
    'Monday': (1, 2),
    'Tuesday': (3, 4),
    'Wednesday': (5, 6),
}
if day not in day_to_col:
    print(f"⚠️ No data available for {day}. Supported days: Monday to Wednesday.")
    exit()

done_col, todo_col = day_to_col[day]

# --- BUILD MESSAGE ---
message = f"📅 **Daily Standup Summary – {day}**\n\n"

for emp in employees:
    name = emp[0]
    done = emp[done_col]
    todo = emp[todo_col]
    message += f"👤 **{name}**\n"
    message += f"✅ *Tasks Accomplished*: {done}\n"
    message += f"🕘 *Tasks for Today*: {todo}\n\n"

# --- SEND TO TEAMS ---
# --- SEND TO TEAMS ---
response = requests.post(WEBHOOK_URL, json={"text": message})

if response.status_code in [200, 202]:
    print("✅ Message successfully sent to Microsoft Teams (status: {})!".format(response.status_code))
else:
    print(f"❌ Failed to send message. Status Code: {response.status_code}")
    print(response.text)


