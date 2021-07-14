from requests import get
from typing import List
from charset_normalizer import detect

if __name__ == "__main__":

    files: List[str] = get("http://127.0.0.1:8080/").json()

    for file in files:
        r = get(
            "http://127.0.0.1:8080/" + file
        )

        if r.ok is False:
            print(f"Unable to retrieve '{file}' | HTTP/{r.status_code}")
            exit(1)

        expected_encoding = detect(r.content)["encoding"]

        if expected_encoding != r.apparent_encoding:
            print(f"Integration test failed | File '{file}' | Expected '{expected_encoding}' got '{r.apparent_encoding}'")
            exit(1)


