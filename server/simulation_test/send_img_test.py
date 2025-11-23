# test_client.py
import requests

url = "http://localhost:9000"

# Test VLM (image interpretation)
files = {"file": open("./test_img/7.jpg", "rb")}
data = {"prompt": "What do you see in this image?"}

resp = requests.post(url + "/get_img_interpretation", files=files, data=data)
print("**"*10)
print("** VLM Test **")

print("VLM:", resp.json())

# Test LLM (text)
print("**"*10)
print("** LLM Test **")
resp2 = requests.post(url + "/get_llm_answer", json={"prompt": "Explain quantum computing simply"})
print("LLM:", resp2.json())
