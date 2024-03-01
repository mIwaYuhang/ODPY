import requests

timeout = 30

try:
    r = requests.post(
        "https://api.mumuglobal.com/api/v1/download/nemux", timeout=timeout,
        data=[
            ("architecture", "x86_64"),
            ("machine", "{}"),
            ("usage", "1"),
        ]
    )

    j = r.json()

    link = j["data"]["mumu"]["link"]

    with open("mumu.txt", "w") as f:
        f.write(link)

except Exception:
    pass
