import requests
res = requests.post("http://localhost:8000/api/chat", json={
    "query": "okay how about cucumbers",
    "device_id": "tablet",
    "store_id": "01400943"
})
print(res.json())
