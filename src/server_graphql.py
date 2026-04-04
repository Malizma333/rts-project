import graphene
from flask import Flask, jsonify, request

import database

app = Flask(__name__)


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


class CreatePost(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int()
        content = graphene.String()

    id = graphene.Int()

    def mutate(self, info, user_id, content):
        post = database.Post.create(user=user_id, content=content)
        return CreatePost(id=post.id)


class RemoveLike(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int()
        post_id = graphene.Int()

    ok = graphene.Boolean()

    def mutate(self, info, user_id, post_id):
        database.Like.delete().where(
            (database.Like.user == user_id) & (database.Like.post == post_id)
        ).execute()
        return RemoveLike(ok=True)


class UpdateStatus(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int()
        status = graphene.String()

    ok = graphene.Boolean()

    def mutate(self, info, user_id, status):
        database.User.update(status=status).where(database.User.id == user_id).execute()
        return UpdateStatus(ok=True)


class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    remove_like = RemoveLike.Field()
    update_status = UpdateStatus.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

app = Flask(__name__)


@app.route("/", methods=["POST"])
def graphql_server():
    data = request.get_json()
    result = schema.execute(data.get("query"))
    return jsonify(
        {
            "data": result.data,
            "errors": [str(e) for e in result.errors] if result.errors else None,
        }
    )
