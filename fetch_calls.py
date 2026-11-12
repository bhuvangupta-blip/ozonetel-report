import os, sys, json, requests
from datetime import datetime, timedelta, timezone

API_KEY = os.environ["OZ_API_KEY"]
USER_NAME = os.environ["OZ_USER"]
WEB_APP_URL = os.environ["WEB_APP_URL"]
SECRET = os.environ["SHEET_SECRET"]

ist = timezone(timedelta(hours=5, minutes=30))
day = (os.environ.get("REPORT_DATE") or "").strip() or \
      (datetime.now(ist) - timedelta(days=1)).strftime("%Y-%m-%d")
print("Fetching calls for", day)

# 1) Ozonetel: GET with a JSON body
oz = requests.get(
    "https://in1-ccaas-api.ozonetel.com/ca_reports/fetchCDRDetails",
    headers={"Content-Type": "application/json", "apiKey": API_KEY},
    data=json.dumps({"userName": USER_NAME,
                     "fromDate": day + " 00:00:00",
                     "toDate": day + " 23:59:59"}),
    timeout=180,
)
print("Ozonetel HTTP", oz.status_code, "| length", len(oz.text))

# 2) Send to the Google Sheet (your existing doPost)
sheet = requests.post(
    WEB_APP_URL,
    json={"secret": SECRET, "date": day, "code": oz.status_code, "text": oz.text},
    timeout=300,
)
print("Sheet:", sheet.text[:500])

if '"status":"success"' not in sheet.text:
    sys.exit("Sheet update failed")
