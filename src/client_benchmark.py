import csv
import datetime
import random
import statistics
import time

import requests

from database import init_db

BASE_REST = "http://localhost:5000"
BASE_GQL = "http://localhost:5001"
BASE_HYBRID = "http://localhost:5002"


def time_request(fn):
    start = time.time()
    res, size = fn()
    elapsed = time.time() - start

    return {
        "time_ms": round(elapsed * 1000, 2),
        "response": res,
        "size_bytes": size,
    }


def test_rest(iterations):
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
            result = requests.post(
                f"{BASE_REST}/post",
                json={
                    "user_id": user_id,
                    "content": "test post",
                },
            )
            return result.json(), len(result.content)

        def update_status():
            result = requests.put(
                f"{BASE_REST}/status",
                json={
                    "user_id": user_id,
                    "status": "idle",
                },
            )
            return result.json(), len(result.content)

        def remove_like():
            result = requests.delete(
                f"{BASE_REST}/like",
                json={
                    "user_id": user_id,
                    "post_id": post_id,
                },
            )
            return result.json(), len(result.content)

        def latest_post():
            user_result = requests.get(f"{BASE_REST}/users/{user_id}")
            user = user_result.json()
            post_result = requests.get(f"{BASE_REST}/posts/{user['posts'][0]}")
            return (
                post_result.json(),
                len(user_result.content) + len(post_result.content),
            )

        def friends():
            user_result = requests.get(f"{BASE_REST}/users/{user_id}")
            size = len(user_result.content)
            friends_list = []
            for id in user_result.json()["friends"]:
                friend_result = requests.get(f"{BASE_REST}/users/{id}")
                size += len(friend_result.content)
                friends_list.append(friend_result.json())
            return friends_list, size

        def latest_friend_comment():
            user_result = requests.get(f"{BASE_REST}/users/{user_id}")
            size = len(user_result.content)

            friends_list = []
            for id in user_result.json()["friends"]:
                friend_result = requests.get(f"{BASE_REST}/users/{id}")
                size += len(friend_result.content)
                friends_list.append(friend_result.json())

            comments_list = []
            for friend in friends_list:
                for id in friend["comments"]:
                    comment_result = requests.get(f"{BASE_REST}/comments/{id}")
                    size += len(comment_result.content)
                    comments_list.append(comment_result.json())

            comments_list.sort(
                key=lambda x: datetime.datetime.fromisoformat(x["created_at"])
            )

            if len(comments_list) == 0:
                return None, size

            return comments_list[-1], size

        results["create_post"].append(time_request(create_post))
        results["update_status"].append(time_request(update_status))
        results["remove_like"].append(time_request(remove_like))
        results["latest_post"].append(time_request(latest_post))
        results["friends"].append(time_request(friends))
        results["latest_friend_comment"].append(time_request(latest_friend_comment))

    return summarize_results(results)


def test_graphql(iterations):
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
            result = requests.post(
                BASE_GQL,
                json={
                    "query": f'mutation {{ createPost(userId: {user_id}, content: "test post") {{ id }} }}'
                },
            )
            return result.json()["data"]["createPost"], len(result.content)

        def update_status():
            result = requests.post(
                BASE_GQL,
                json={
                    "query": f'mutation {{ updateStatus(userId: {user_id}, status: "idle") {{ ok }} }}'
                },
            )
            return result.json()["data"]["updateStatus"], len(result.content)

        def remove_like():
            result = requests.post(
                BASE_GQL,
                json={
                    "query": f"mutation {{ removeLike(userId: {user_id}, postId: {post_id}) {{ ok }} }}"
                },
            )
            return result.json()["data"]["removeLike"], len(result.content)

        def latest_post():
            result = requests.post(
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
            )
            return result.json()["data"]["user"]["posts"][0], len(result.content)

        def friends():
            result = requests.post(
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
            )
            return result.json()["data"]["user"]["friends"], len(result.content)

        def latest_friend_comment():
            friend_result = requests.post(
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
            )
            friends = friend_result.json()["data"]["user"]["friends"]
            comments = []
            for friend in friends:
                comments.extend(friend["comments"])
            comments.sort(key=lambda x: datetime.datetime.fromisoformat(x["createdAt"]))
            if len(comments) == 0:
                return None, len(friend_result.content)
            return comments[-1], len(friend_result.content)

        results["create_post"].append(time_request(create_post))
        results["update_status"].append(time_request(update_status))
        results["remove_like"].append(time_request(remove_like))
        results["latest_post"].append(time_request(latest_post))
        results["friends"].append(time_request(friends))
        results["latest_friend_comment"].append(time_request(latest_friend_comment))

    return summarize_results(results)


def test_hybrid(iterations):
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
            result = requests.post(
                f"{BASE_HYBRID}/post",
                json={
                    "user_id": user_id,
                    "content": "test post",
                },
            )
            return result.json(), len(result.content)

        def update_status():
            result = requests.put(
                f"{BASE_HYBRID}/status",
                json={
                    "user_id": user_id,
                    "status": "idle",
                },
            )
            return result.json(), len(result.content)

        def remove_like():
            result = requests.delete(
                f"{BASE_HYBRID}/like",
                json={
                    "user_id": user_id,
                    "post_id": post_id,
                },
            )
            return result.json(), len(result.content)

        def latest_post():
            result = requests.post(
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
            )
            return result.json()["data"]["user"]["posts"][0], len(result.content)

        def friends():
            result = requests.post(
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
            )
            return result.json()["data"]["user"]["friends"], len(result.content)

        def latest_friend_comment():
            friend_result = requests.post(
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
            )
            friends = friend_result.json()["data"]["user"]["friends"]
            comments = []
            for friend in friends:
                comments.extend(friend["comments"])
            comments.sort(key=lambda x: datetime.datetime.fromisoformat(x["createdAt"]))
            if len(comments) == 0:
                return None, len(friend_result.content)
            return comments[-1], len(friend_result.content)

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
        times = [call["time_ms"] for call in calls]
        sizes = [call["size_bytes"] for call in calls]

        summary[key] = [
            statistics.mean(times),
            min(times),
            max(times),
            statistics.mean(sizes),
            min(sizes),
            max(sizes),
        ]

    return summary


def create_csvs(rest, gql, hybrid):
    servers = (("REST", rest), ("GraphQL", gql), ("Hybrid", hybrid))
    methods = (
        "create_post",
        "remove_like",
        "update_status",
        "latest_post",
        "friends",
        "latest_friend_comment",
    )

    csv_data = [
        [
            "Server",
            "Method",
            "Average RT (ms)",
            "Min RT (ms)",
            "Max RT (ms)",
            "Average Size (bytes)",
            "Min Size (bytes)",
            "Max Size (bytes)",
        ]
    ]

    for server in servers:
        for method in methods:
            csv_data.append([server[0], method, *server[1][method]])

    with open("out/overall_summary.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)

    csv_data = [["Method", "REST", "GraphQL", "Hybrid"]]

    for method in methods:
        csv_data.append([method, rest[method][0], gql[method][0], hybrid[method][0]])

    with open("out/average_times.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)

    csv_data = [["Method", "REST", "GraphQL", "Hybrid"]]

    for method in methods:
        csv_data.append([method, rest[method][3], gql[method][3], hybrid[method][3]])

    with open("out/average_sizes.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)


def main():
    SEED = 20
    ITERATIONS = 100
    random.seed(SEED)
    init_db()
    print("Testing REST...")
    rest = test_rest(ITERATIONS)
    random.seed(SEED)
    init_db()
    print("Testing GraphQL...")
    graphql = test_graphql(ITERATIONS)
    random.seed(SEED)
    init_db()
    print("Testing Hybrid...")
    hybrid = test_hybrid(ITERATIONS)

    create_csvs(rest, graphql, hybrid)


if __name__ == "__main__":
    main()
