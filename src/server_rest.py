from flask import Flask, jsonify, request
import database

app = Flask(__name__)

@app.route("/create_post", methods=["POST"])
def create_post():
    data = request.json
    post = database.Post.create(user=data["user_id"], content=data["content"])
    return jsonify({"id": post.id})


@app.route("/remove_like", methods=["DELETE"])
def remove_like():
    data = request.json
    database.Like.delete().where(
        (database.Like.user == data["user_id"]) & (database.Like.post == data["post_id"])
    ).execute()
    return jsonify({"status": "ok"})


@app.route("/update_status", methods=["PUT"])
def update_status():
    data = request.json
    database.User.update(status=data["status"]).where(database.User.id == data["user_id"]).execute()
    return jsonify({"status": "ok"})


@app.route("/latest_post/<int:user_id>")
def latest_post(user_id):
    post = (
        database.Post.select()
        .where(database.Post.user == user_id)
        .order_by(database.Post.created_at.desc())
        .first()
    )
    return jsonify({"content": post.content if post else None})


@app.route("/friends/<int:user_id>")
def friends(user_id):
    friends = database.Friendship.select().where(database.Friendship.user == user_id)
    return jsonify([f.friend.id for f in friends])


@app.route("/latest_friend_comment/<int:user_id>")
def latest_friend_comment(user_id):
    friends = database.Friendship.select(database.Friendship.friend).where(database.Friendship.user == user_id)
    comment = (
        database.Comment.select()
        .where(database.Comment.user.in_(friends))
        .order_by(database.Comment.created_at.desc())
        .first()
    )
    return jsonify({"content": comment.content if comment else None})
