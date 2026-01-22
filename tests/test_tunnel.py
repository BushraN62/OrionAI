import requests

r = requests.get(
    "https://llm.theorionai.net/api/tags",
    headers={
        "CF-Access-Client-Id":    "4640d113d67831e5a77354d7835b4950",      # no .access
        "CF-Access-Client-Secret":"afe8518726e621e1ab9067623855da446f21fde1088b161614ee6f613b4ad3b3",
    },
    timeout=30,
)
print(r.status_code, r.text)
