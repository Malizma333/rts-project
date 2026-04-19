import graphene
from flask import Flask, jsonify, request

import database

app = Flask(__name__)


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
