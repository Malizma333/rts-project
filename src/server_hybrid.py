import graphene
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
        (database.Like.user == data["user_id"])
        & (database.Like.post == data["post_id"])
    ).execute()
    return jsonify({"status": "ok"})


@app.route("/update_status", methods=["PUT"])
def update_status():
    data = request.json
    database.User.update(status=data["status"]).where(
        database.User.id == data["user_id"]
    ).execute()
    return jsonify({"status": "ok"})


class PostType(graphene.ObjectType):
    id = graphene.Int()
    content = graphene.String()


class Query(graphene.ObjectType):
    latest_post = graphene.Field(PostType, user_id=graphene.Int())
    friends = graphene.List(graphene.Int, user_id=graphene.Int())
    latest_friend_comment = graphene.String(user_id=graphene.Int())

    def resolve_latest_post(self, info, user_id):
        post = (
            database.Post.select()
            .where(database.Post.user == user_id)
            .order_by(database.Post.created_at.desc())
            .first()
        )
        return post

    def resolve_friends(self, info, user_id):
        return [
            f.friend.id
            for f in database.Friendship.select().where(
                database.Friendship.user == user_id
            )
        ]

    def resolve_latest_friend_comment(self, info, user_id):
        friends = database.Friendship.select(database.Friendship.friend).where(
            database.Friendship.user == user_id
        )
        comment = (
            database.Comment.select()
            .where(database.Comment.user.in_(friends))
            .order_by(database.Comment.created_at.desc())
            .first()
        )
        return comment.content if comment else None


schema = graphene.Schema(query=Query)


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    result = schema.execute(data.get("query"))
    return jsonify(
        {
            "data": result.data,
            "errors": [str(e) for e in result.errors] if result.errors else None,
        }
    )
