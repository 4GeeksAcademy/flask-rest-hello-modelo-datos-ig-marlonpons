from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(50))
    lastname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    posts: Mapped[List["Post"]] = relationship("Post", back_populates="user")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="author")


    following: Mapped[List["User"]] = relationship("User",secondary="follower",primaryjoin="User.id == Follower.user_from_id",
                                                    secondaryjoin="User.id == Follower.user_to_id",
                                                    back_populates="followers"
    )

    followers: Mapped[List["User"]] = relationship("User",secondary="follower",primaryjoin="User.id == Follower.user_to_id",
                                                    secondaryjoin="User.id == Follower.user_from_id",
                                                    back_populates="following"
    )
    """
    "User"---Relacion con otros usuarios (autoreferencia).
    secondary="followe"----Nombre de la tabla intermedia que conecta los usuarios.
    primaryjoin---Define cómo se conecta este usuario con la tabla follower. En este caso: User.id == Follower.user_from_id → el usuario actual es el que sigue a otros.
    secondaryjoin------Define cómo llegar a los otros usuarios desde la tabla follower. Aquí: User.id == Follower.user_to_id → los usuarios a los que sigo.
    back_populates="followers"---------Relación inversa: los usuarios que me siguen a mí.
    """

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    
class Post(db.Model):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'))

    user: Mapped["User"] = relationship("User", back_populates="posts")
    media: Mapped[List["Media"]] = relationship("Media", back_populates="post")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="post")


    def serialize(self):
        return{
            "id" : self.id,
            "user_id" : self.user_id
        }


class Media(db.Model):
    __tablename__ = 'media'

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(Enum('image','video', name='media_type'))
    url: Mapped[str] = mapped_column(String(300),nullable=False)
    post_id: Mapped[int] = mapped_column(db.ForeignKey('post.id'))

    post: Mapped["Post"] = relationship("Post", back_populates = "media")

    def serialize(self):
        return{
            "id": self.id,
            "type": self.type,
            "url": self.url,
            "post_id": self.post_id
        }


class Comment(db.Model):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True)
    comment_text:Mapped[str] = mapped_column(String(500), nullable=False)
    author_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'))
    post_id: Mapped[int] = mapped_column(db.ForeignKey('post.id'))
    
    author : Mapped["User"] = relationship("User", back_populates="comments")
    post : Mapped["Post"] = relationship("Post", back_populates="comments")
    
    def serialize(self):
        return{
            "id": self.id,
            "comment_text": self.comment_text,
            "author_id": self.author_id,
            "post_id": self.post_id
        }

     
class Follower(db.Model):
    __tablename__ = 'follower'

    user_from_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), primary_key=True)
    user_to_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), primary_key=True)
     
    user_from: Mapped["User"] = relationship("User", foreign_keys=[user_from_id], back_populates="following")
    user_to: Mapped["User"] = relationship("User", foreign_keys=[user_to_id], back_populates="followers")

    def serialize(self):
        return {
            "user_from_id": self.user_from_id,
            "user_to_id": self.user_to_id
        }

