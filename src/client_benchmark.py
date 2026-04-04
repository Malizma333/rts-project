import random
import time

import matplotlib.pyplot as plt
import requests

BASE_REST = "http://localhost:5000"
BASE_GQL = "http://localhost:5001"
BASE_HYBRID = "http://localhost:5002"


def time_request(fn):
    start = time.time()
    res = fn()
    elapsed = time.time() - start

    try:
        data = res.json()
    except Exception:
        data = res.text

    return {
        "status_code": res.status_code,
        "time_ms": round(elapsed * 1000, 2),
        "response": data,
    }


def rand_user():
    return random.randint(1, 1000)


def rand_post():
    return random.randint(1, 1000)


def test_rest(iterations=50):
    results = {
        "create_post": [],
        "remove_like": [],
        "update_status": [],
        "latest_post": [],
        "friends": [],
        "latest_friend_comment": [],
    }

    for _ in range(iterations):
        user_id = rand_user()
        post_id = rand_post()

        results["create_post"].append(
            time_request(
                lambda: requests.post(
                    f"{BASE_REST}/create_post",
                    json={
                        "user_id": user_id,
                        "content": f"test post {random.randint(1, 100000)}",
                    },
                )
            )
        )

        results["update_status"].append(
            time_request(
                lambda: requests.put(
                    f"{BASE_REST}/update_status",
                    json={
                        "user_id": user_id,
                        "status": f"status {random.randint(1, 100000)}",
                    },
                )
            )
        )

        results["remove_like"].append(
            time_request(
                lambda: requests.delete(
                    f"{BASE_REST}/remove_like",
                    json={
                        "user_id": user_id,
                        "post_id": post_id,
                    },
                )
            )
        )

        results["latest_post"].append(
            time_request(lambda: requests.get(f"{BASE_REST}/latest_post/{user_id}"))
        )

        results["friends"].append(
            time_request(lambda: requests.get(f"{BASE_REST}/friends/{user_id}"))
        )

        results["latest_friend_comment"].append(
            time_request(
                lambda: requests.get(f"{BASE_REST}/latest_friend_comment/{user_id}")
            )
        )

    return summarize_results(results)


def test_graphql(iterations=50):
    results = {
        "create_post": [],
        "remove_like": [],
        "update_status": [],
        "latest_post": [],
        "friends": [],
        "latest_friend_comment": [],
    }

    for _ in range(iterations):
        user_id = rand_user()
        post_id = rand_post()

        results["create_post"].append(
            time_request(
                lambda: requests.post(
                    BASE_GQL,
                    json={
                        "query": f'mutation {{ createPost(userId: {user_id}, content: "test post {random.randint(1, 100000)}") {{ id }} }}'
                    },
                )
            )
        )

        results["update_status"].append(
            time_request(
                lambda: requests.post(
                    BASE_GQL,
                    json={
                        "query": f'mutation {{ updateStatus(userId: {user_id}, status: "status {random.randint(1, 100000)}") {{ ok }} }}'
                    },
                )
            )
        )

        results["remove_like"].append(
            time_request(
                lambda: requests.post(
                    BASE_GQL,
                    json={
                        "query": f"mutation {{ removeLike(userId: {user_id}, postId: {post_id}) {{ ok }} }}"
                    },
                )
            )
        )

        results["latest_post"].append(
            time_request(
                lambda: requests.post(
                    BASE_GQL,
                    json={
                        "query": f"{{ latestPost(userId: {user_id}) {{ id content }} }}"
                    },
                )
            )
        )

        results["friends"].append(
            time_request(
                lambda: requests.post(
                    BASE_GQL,
                    json={"query": f"{{ friends(userId: {user_id}) }}"},
                )
            )
        )

        results["latest_friend_comment"].append(
            time_request(
                lambda: requests.post(
                    BASE_GQL,
                    json={"query": f"{{ latestFriendComment(userId: {user_id}) }}"},
                )
            )
        )

    return summarize_results(results)


def test_hybrid(iterations=50):
    results = {
        "create_post": [],
        "remove_like": [],
        "update_status": [],
        "latest_post": [],
        "friends": [],
        "latest_friend_comment": [],
    }

    for _ in range(iterations):
        user_id = rand_user()
        post_id = rand_post()

        results["create_post"].append(
            time_request(
                lambda: requests.post(
                    f"{BASE_HYBRID}/create_post",
                    json={
                        "user_id": user_id,
                        "content": f"hybrid post {random.randint(1, 100000)}",
                    },
                )
            )
        )

        results["update_status"].append(
            time_request(
                lambda: requests.put(
                    f"{BASE_HYBRID}/update_status",
                    json={
                        "user_id": user_id,
                        "status": f"status {random.randint(1, 100000)}",
                    },
                )
            )
        )

        results["remove_like"].append(
            time_request(
                lambda: requests.delete(
                    f"{BASE_HYBRID}/remove_like",
                    json={
                        "user_id": user_id,
                        "post_id": post_id,
                    },
                )
            )
        )

        results["latest_post"].append(
            time_request(
                lambda: requests.post(
                    f"{BASE_HYBRID}/graphql",
                    json={
                        "query": f"{{ latestPost(userId: {user_id}) {{ id content }} }}"
                    },
                )
            )
        )

        results["friends"].append(
            time_request(
                lambda: requests.post(
                    f"{BASE_HYBRID}/graphql",
                    json={"query": f"{{ friends(userId: {user_id}) }}"},
                )
            )
        )

        results["latest_friend_comment"].append(
            time_request(
                lambda: requests.post(
                    f"{BASE_HYBRID}/graphql",
                    json={"query": f"{{ latestFriendComment(userId: {user_id}) }}"},
                )
            )
        )

    return summarize_results(results)


def summarize_results(results):
    summary = {}

    for key, calls in results.items():
        times = [c["time_ms"] for c in calls]
        success = [
            c
            for c in calls
            if c["status_code"] == 200 and "errors" not in str(c["response"])
        ]

        summary[key] = {
            "avg_ms": round(sum(times) / len(times), 2),
            "min_ms": min(times),
            "max_ms": max(times),
            "success_rate": f"{len(success)}/{len(calls)}",
        }

    return summary


def create_plots(rest, gql, hybrid):
    operations = sorted(set(rest.keys()) | set(gql.keys()) | set(hybrid.keys()))

    for op in operations:
        plt.figure()

        values = [
            rest.get(op, {}).get("avg_ms", 0),
            gql.get(op, {}).get("avg_ms", 0),
            hybrid.get(op, {}).get("avg_ms", 0),
        ]

        labels = ["REST", "GraphQL", "Hybrid"]

        plt.bar(labels, values)
        plt.ylabel("Average Response Time (ms)")
        plt.title(f"{op} Performance")

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    from pprint import pprint

    from database import init_db

    init_db()
    rest = test_rest(100)
    init_db()
    graphql = test_graphql(100)
    init_db()
    hybrid = test_hybrid(100)

    pprint({"REST": rest, "GraphQL": graphql, "Hybrid": hybrid})
    create_plots(rest, graphql, hybrid)
