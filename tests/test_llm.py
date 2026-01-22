import os, requests, json
from dotenv import load_dotenv
load_dotenv()   # will read .env from the project root

BASE = "https://llm.theorionai.net"
HEADERS = {
  "CF-Access-Client-Id": os.getenv("CF_ACCESS_CLIENT_ID"),
  "CF-Access-Client-Secret": os.getenv("CF_ACCESS_CLIENT_SECRET"),
}

r = requests.get(f"{BASE}/api/tags", headers=HEADERS, timeout=60)
print("Status:", r.status_code)
print("Text:", r.text)
