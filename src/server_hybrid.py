import graphene
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


class CommentType(graphene.ObjectType):
    id = graphene.Int()
    content = graphene.String()
    created_at = graphene.String()


class PostType(graphene.ObjectType):
    id = graphene.Int()
    content = graphene.String()


class UserType(graphene.ObjectType):
    id = graphene.Int()
    username = graphene.String()
    status = graphene.String()

    friends = graphene.List(lambda: UserType)
    posts = graphene.List(PostType)
    comments = graphene.List(CommentType)

    def resolve_friends(self, info):
        return resolve_friends(self, info)

    def resolve_posts(self, info):
        return resolve_posts(self, info)

    def resolve_comments(self, info):
        return resolve_comments(self, info)


def resolve_friends(parent, info):
    return [
        f.friend
        for f in database.Friendship.select().where(
            database.Friendship.user == parent.id
        )
    ]


def resolve_posts(parent, info):
    return (
        database.Post.select()
        .where(database.Post.user == parent.id)
        .order_by(database.Post.created_at.desc())
    )


def resolve_comments(parent, info):
    return (
        database.Comment.select()
        .where(database.Comment.user == parent.id)
        .order_by(database.Comment.created_at.desc())
    )


class Query(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.Int(required=True))

    def resolve_user(self, info, id):
        return database.User.get_by_id(id)


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
