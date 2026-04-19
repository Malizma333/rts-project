from flask import Flask, jsonify, request

import database

app = Flask(__name__)


@app.route("/post", methods=["POST"])
def create_post():
    data = request.json
    post = database.Post.create(user=data["user_id"], content=data["content"])
    return jsonify({"id": post.id})


@app.route("/like", methods=["DELETE"])
def remove_like():
    data = request.json
    database.Like.delete().where(
        (database.Like.user == data["user_id"])
        & (database.Like.post == data["post_id"])
    ).execute()
    return jsonify({"status": "ok"})


@app.route("/status", methods=["PUT"])
def update_status():
    data = request.json
    database.User.update(status=data["status"]).where(
        database.User.id == data["user_id"]
    ).execute()
    return jsonify({"status": "ok"})


@app.route("/users/<int:user_id>")
def get_user(user_id):
    user = database.User.get_by_id(user_id)

    # Friend IDs (people this user added)
    friend_ids = [
        f.friend.id
        for f in database.Friendship.select().where(database.Friendship.user == user)
    ]

    # Post IDs
    post_ids = [
        post.id for post in database.Post.select().where(database.Post.user == user)
    ]

    # Like IDs
    like_ids = [
        like.id for like in database.Like.select().where(database.Like.user == user)
    ]

    # Comment IDs
    comment_ids = [
        c.id for c in database.Comment.select().where(database.Comment.user == user)
    ]

    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "status": user.status,
            "friends": friend_ids,
            "posts": post_ids,
            "likes": like_ids,
            "comments": comment_ids,
        }
    )


@app.route("/comments/<int:comment_id>")
def comment(comment_id):
    c = database.Comment.get_by_id(comment_id)

    return jsonify(
        {
            "id": c.id,
            "content": c.content,
            "created_at": c.created_at.isoformat(),
        }
    )


@app.route("/posts/<int:post_id>")
def post(post_id):
    p = database.Post.get_by_id(post_id)

    return jsonify(
        {
            "id": p.id,
            "content": p.content,
            "created_at": p.created_at.isoformat(),
        }
    )
