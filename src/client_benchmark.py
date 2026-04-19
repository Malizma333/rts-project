import csv
import datetime
import random
import time

import matplotlib as mpl
import matplotlib.pyplot as plt
import requests

from database import init_db

BASE_REST = "http://localhost:5000"
BASE_GQL = "http://localhost:5001"
BASE_HYBRID = "http://localhost:5002"


def time_request(fn):
    start = time.time()
    res = fn()
    elapsed = time.time() - start

    return {
        "time_ms": round(elapsed * 1000, 2),
        "response": res,
    }


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
        user_id = random.randint(1, 1000)
        post_id = random.randint(1, 1000)

        def create_post():
            return requests.post(
                f"{BASE_REST}/post",
                json={
                    "user_id": user_id,
                    "content": "test post",
                },
            ).json()

        def update_status():
            return requests.put(
                f"{BASE_REST}/status",
                json={
                    "user_id": user_id,
                    "status": "idle",
                },
            ).json()

        def remove_like():
            requests.delete(
                f"{BASE_REST}/like",
                json={
                    "user_id": user_id,
                    "post_id": post_id,
                },
            ).json()

        def latest_post():
            user = requests.get(f"{BASE_REST}/users/{user_id}").json()
            post = requests.get(f"{BASE_REST}/posts/{user['posts'][0]}").json()
            return post

        def friends():
            user = requests.get(f"{BASE_REST}/users/{user_id}").json()
            friends_list = []
            for id in user["friends"]:
                friends_list.append(requests.get(f"{BASE_REST}/users/{id}").json())
            return friends_list

        def latest_friend_comment():
            user = requests.get(f"{BASE_REST}/users/{user_id}").json()
            friends_list = []
            for id in user["friends"]:
                friends_list.append(requests.get(f"{BASE_REST}/users/{id}").json())
            comments_list = []
            for friend in friends_list:
                for id in friend["comments"]:
                    comments_list.append(
                        requests.get(f"{BASE_REST}/comments/{id}").json()
                    )
            comments_list.sort(
                key=lambda x: datetime.datetime.fromisoformat(x["created_at"])
            )
            if len(comments_list) == 0:
                return None
            return comments_list[-1]

        results["create_post"].append(time_request(create_post))
        results["update_status"].append(time_request(update_status))
        results["remove_like"].append(time_request(remove_like))
        results["latest_post"].append(time_request(latest_post))
        results["friends"].append(time_request(friends))
        results["latest_friend_comment"].append(time_request(latest_friend_comment))

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
        user_id = random.randint(1, 1000)
        post_id = random.randint(1, 1000)

        def create_post():
            return requests.post(
                BASE_GQL,
                json={
                    "query": f'mutation {{ createPost(userId: {user_id}, content: "test post") {{ id }} }}'
                },
            ).json()["data"]["createPost"]

        def update_status():
            return requests.post(
                BASE_GQL,
                json={
                    "query": f'mutation {{ updateStatus(userId: {user_id}, status: "idle") {{ ok }} }}'
                },
            ).json()["data"]["updateStatus"]

        def remove_like():
            return requests.post(
                BASE_GQL,
                json={
                    "query": f"mutation {{ removeLike(userId: {user_id}, postId: {post_id}) {{ ok }} }}"
                },
            ).json()["data"]["removeLike"]

        def latest_post():
            return requests.post(
                BASE_GQL,
                json={
                    "query": f"""
                    {{
                    user(id: {user_id}) {{
                        posts {{
                        id
                        content
                        }}
                    }}
                    }}
                    """
                },
            ).json()["data"]["user"]["posts"][0]

        def friends():
            return requests.post(
                BASE_GQL,
                json={
                    "query": f"""
                    {{
                    user(id: {user_id}) {{
                        friends {{
                            username
                        }}
                    }}
                    }}
                    """
                },
            ).json()["data"]["user"]["friends"]

        def latest_friend_comment():
            friends = requests.post(
                BASE_GQL,
                json={
                    "query": f"""
                    {{
                    user(id: {user_id}) {{
                        friends {{
                        comments {{
                            content
                            createdAt
                        }}
                        }}
                    }}
                    }}
                    """
                },
            ).json()["data"]["user"]["friends"]
            comments = []
            for friend in friends:
                comments.extend(friend["comments"])
            comments.sort(
                key=lambda x: datetime.datetime.fromisoformat(x["createdAt"])
            )
            if len(comments) == 0:
                return None
            return comments[-1]

        results["create_post"].append(time_request(create_post))
        results["update_status"].append(time_request(update_status))
        results["remove_like"].append(time_request(remove_like))
        results["latest_post"].append(time_request(latest_post))
        results["friends"].append(time_request(friends))
        results["latest_friend_comment"].append(time_request(latest_friend_comment))

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
        user_id = random.randint(1, 1000)
        post_id = random.randint(1, 1000)

        def create_post():
            return requests.post(
                f"{BASE_HYBRID}/post",
                json={
                    "user_id": user_id,
                    "content": "test post",
                },
            ).json()

        def update_status():
            return requests.put(
                f"{BASE_HYBRID}/status",
                json={
                    "user_id": user_id,
                    "status": "idle",
                },
            ).json()

        def remove_like():
            requests.delete(
                f"{BASE_HYBRID}/like",
                json={
                    "user_id": user_id,
                    "post_id": post_id,
                },
            ).json()

        def latest_post():
            return requests.post(
                f"{BASE_HYBRID}/graphql",
                json={
                    "query": f"""
                    {{
                    user(id: {user_id}) {{
                        posts {{
                        id
                        content
                        }}
                    }}
                    }}
                    """
                },
            ).json()["data"]["user"]["posts"][0]

        def friends():
            return requests.post(
                f"{BASE_HYBRID}/graphql",
                json={
                    "query": f"""
                    {{
                    user(id: {user_id}) {{
                        friends {{
                            username
                        }}
                    }}
                    }}
                    """
                },
            ).json()["data"]["user"]["friends"]

        def latest_friend_comment():
            friends = requests.post(
                f"{BASE_HYBRID}/graphql",
                json={
                    "query": f"""
                    {{
                    user(id: {user_id}) {{
                        friends {{
                            comments {{
                                content
                                createdAt
                            }}
                        }}
                    }}
                    }}
                    """
                },
            ).json()["data"]["user"]["friends"]
            comments = []
            for friend in friends:
                comments.extend(friend["comments"])
            comments.sort(
                key=lambda x: datetime.datetime.fromisoformat(x["createdAt"])
            )
            if len(comments) == 0:
                return None
            return comments[-1]

        results["create_post"].append(time_request(create_post))
        results["update_status"].append(time_request(update_status))
        results["remove_like"].append(time_request(remove_like))
        results["latest_post"].append(time_request(latest_post))
        results["friends"].append(time_request(friends))
        results["latest_friend_comment"].append(time_request(latest_friend_comment))

    return summarize_results(results)


def summarize_results(results):
    summary = {}

    for key, calls in results.items():
        print(key, calls)
        times = [call["time_ms"] for call in calls]

        if len(times) == 0:
            avg = 0
        else:
            avg = round(sum(times) / len(times), 2)

        summary[key] = {
            "avg_ms": avg,
            "min_ms": round(min(times), 2),
            "max_ms": round(max(times), 2),
        }

    return summary


def create_plots(rest, gql, hybrid):
    operations = sorted(set(rest.keys()) | set(gql.keys()) | set(hybrid.keys()))

    mpl.rcParams["font.size"] = 18
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
        plt.title(f"{op}")

        plt.tight_layout()
        plt.savefig(f"out/{op}.png", bbox_inches="tight")


def create_csvs(rest, gql, hybrid):
    csv_data = [
        [
            "Server",
            "Method",
            "Average RT (ms)",
            "Max RT (ms)",
            "Min RT (ms)",
        ]
    ]

    for server in (("REST", rest), ("GraphQL", gql), ("Hybrid", hybrid)):
        for method in (
            "create_post",
            "remove_like",
            "update_status",
            "latest_post",
            "friends",
            "latest_friend_comment",
        ):
            csv_data.append(
                [
                    server[0],
                    method,
                    server[1][method]["avg_ms"],
                    server[1][method]["max_ms"],
                    server[1][method]["min_ms"],
                ]
            )

    with open("out/summary.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)

    csv_data = [
        [
            "Method",
            "REST",
            "GraphQL",
            "Hybrid",
        ]
    ]

    for method in (
        "create_post",
        "remove_like",
        "update_status",
        "latest_post",
        "friends",
        "latest_friend_comment",
    ):
        csv_data.append(
            [
                method,
                rest[method]["avg_ms"],
                gql[method]["avg_ms"],
                hybrid[method]["avg_ms"],
            ]
        )

    with open("out/averages.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)


def main():
    SEED = 20
    random.seed(SEED)
    init_db()
    print("Testing REST...")
    rest = test_rest(100)
    random.seed(SEED)
    init_db()
    print("Testing GraphQL...")
    graphql = test_graphql(100)
    random.seed(SEED)
    init_db()
    print("Testing Hybrid...")
    hybrid = test_hybrid(100)

    create_csvs(rest, graphql, hybrid)
    # create_plots(rest, graphql, hybrid)


if __name__ == "__main__":
    main()
