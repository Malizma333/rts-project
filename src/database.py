import os
import random
import string
from datetime import datetime, timedelta

import peewee

DATABASE = peewee.SqliteDatabase("app.db")
connected = False


class BaseModel(peewee.Model):
    class Meta:
        database = DATABASE


class User(BaseModel):
    id = peewee.AutoField()
    username = peewee.CharField()
    status = peewee.TextField(null=True)


class Post(BaseModel):
    id = peewee.AutoField()
    user = peewee.ForeignKeyField(User, backref="posts")
    content = peewee.TextField()
    created_at = peewee.DateTimeField(
        constraints=[peewee.SQL("DEFAULT CURRENT_TIMESTAMP")]
    )


class Like(BaseModel):
    id = peewee.AutoField()
    user = peewee.ForeignKeyField(User)
    post = peewee.ForeignKeyField(Post)


class Friendship(BaseModel):
    id = peewee.AutoField()
    user = peewee.ForeignKeyField(User, backref="friends")
    friend = peewee.ForeignKeyField(User)


class Comment(BaseModel):
    id = peewee.AutoField()
    user = peewee.ForeignKeyField(User)
    post = peewee.ForeignKeyField(Post)
    content = peewee.TextField()
    created_at = peewee.DateTimeField(
        constraints=[peewee.SQL("DEFAULT CURRENT_TIMESTAMP")]
    )


def init_db():
    global connected
    if connected:
        DATABASE.close()
        os.remove("app.db")
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Like, Friendship, Comment])
    connected = True
    seed(DATABASE)


def random_string(length=10):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_sentence(words=8):
    return " ".join(random_string(random.randint(3, 8)) for _ in range(words))


def random_timestamp():
    now = datetime.now()
    delta = timedelta(days=random.randint(0, 365), seconds=random.randint(0, 86400))
    return now - delta


def seed(db, n=1000):
    print("Seeding database...")

    with db.atomic():
        users = []
        for i in range(n):
            users.append(
                {
                    "username": f"user_{i}_{random_string(5)}",
                    "status": random_sentence(6) if random.random() > 0.3 else None,
                }
            )
        User.insert_many(users).execute()

    users = list(User.select())

    with db.atomic():
        posts = []
        for _ in range(n):
            user = random.choice(users)
            posts.append(
                {
                    "user": user.id,
                    "content": random_sentence(12),
                    "created_at": random_timestamp(),
                }
            )
        Post.insert_many(posts).execute()

    posts = list(Post.select())

    with db.atomic():
        likes = []
        for _ in range(n):
            user = random.choice(users)
            post = random.choice(posts)
            likes.append(
                {
                    "user": user.id,
                    "post": post.id,
                }
            )
        Like.insert_many(likes).execute()

    with db.atomic():
        friendships = set()
        rows = []

        while len(rows) < n:
            u1, u2 = random.sample(users, 2)
            pair = (u1.id, u2.id)

            # avoid duplicates
            if pair not in friendships:
                friendships.add(pair)
                rows.append(
                    {
                        "user": u1.id,
                        "friend": u2.id,
                    }
                )

        Friendship.insert_many(rows).execute()

    with db.atomic():
        comments = []
        for _ in range(n):
            user = random.choice(users)
            post = random.choice(posts)
            comments.append(
                {
                    "user": user.id,
                    "post": post.id,
                    "content": random_sentence(10),
                    "created_at": random_timestamp(),
                }
            )
        Comment.insert_many(comments).execute()

    print("Seeding complete.")


if __name__ == "__main__":
    init_db()
