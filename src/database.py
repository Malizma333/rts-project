import peewee

DATABASE = peewee.PostgresqlDatabase(
    "testdb", user="postgres", password="password", host="localhost", port=5432
)


class BaseModel(peewee.Model):
    class Meta:
        database = DATABASE


class User(BaseModel):
    username = peewee.CharField()
    status = peewee.TextField(null=True)


class Post(BaseModel):
    user = peewee.ForeignKeyField(User, backref="posts")
    content = peewee.TextField()
    created_at = peewee.DateTimeField(
        constraints=[peewee.SQL("DEFAULT CURRENT_TIMESTAMP")]
    )


class Like(BaseModel):
    user = peewee.ForeignKeyField(User)
    post = peewee.ForeignKeyField(Post)


class Friendship(BaseModel):
    user = peewee.ForeignKeyField(User, backref="friends")
    friend = peewee.ForeignKeyField(User)


class Comment(BaseModel):
    user = peewee.ForeignKeyField(User)
    post = peewee.ForeignKeyField(Post)
    content = peewee.TextField()
    created_at = peewee.DateTimeField(
        constraints=[peewee.SQL("DEFAULT CURRENT_TIMESTAMP")]
    )


def init_db():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Like, Friendship, Comment])


if __name__ == "__main__":
    init_db()
