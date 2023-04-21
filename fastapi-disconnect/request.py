import httpx

HOST = "http://127.0.0.1:8000/put"


def main():
    client = httpx.Client()
    r = client.put(HOST, json={"message": "Hello boys"})
    print(r, r.text)


main()
