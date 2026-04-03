import time

import requests

BASE_REST = "http://localhost:5000"
BASE_GQL = "http://localhost:5000/graphql"


def time_request(fn, repeats=1):
    start = time.time()
    for _ in range(repeats):
        fn()
    return (time.time() - start) / repeats


def test_rest():
    return {
        "create_post": time_request(
            lambda: requests.post(
                f"{BASE_REST}/create_post", json={"user_id": 1, "content": "hi"}
            )
        ),
        "latest_post": time_request(lambda: requests.get(f"{BASE_REST}/latest_post/1")),
    }


def test_graphql():
    return {
        "latest_post": time_request(
            lambda: requests.post(
                BASE_GQL, json={"query": "{ latestPost(userId:1){ id content } }"}
            )
        )
    }


def test_hybrid():
    return None


if __name__ == "__main__":
    print("REST:", test_rest())
    print("GraphQL:", test_graphql())
    print("Hybrid:", test_hybrid())
