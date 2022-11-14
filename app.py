# Импорт необходимых модулей
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from create_data import Movie, Director, Genre

# Создание приложения Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Схема фильмов
class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()


# Схема режиссеров
class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


# Схема жанров
class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


# все схемы для работы с вьюшками
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

# Создание API
api = Api(app)
# Все неймспейсы
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


# Вью класс для всех фильмов
@movie_ns.route('/')
class MoviesView(Resource):
    def get(self, page=1):
        all_movies = db.session.query(Movie)

        director_id = request.args.get("director_id")
        if director_id is not None:
            all_movies = all_movies.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            all_movies = all_movies.filter(Movie.genre_id == genre_id)

        movies = all_movies.paginate(page, per_page=3)
        return movies_schema.dump(movies.items), 200

    def post(self):
        request_json = request.json
        new_movie = Movie(**request_json)

        with db.session.begin():
            db.session.add(new_movie)

        return "", 201


# Вью класс для фильмов по id
@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return "", 404
        return movie_schema.dump(movie), 200

    def put(self, mid: int):
        update_row = db.session.query(Movie).filter(Movie.id == mid).update(request.json)

        if update_row != 1:
            return "", 404

        db.session.commit()

        return "", 204

    def delete(self, mid: int):
        delete_rows = db.session.query(Movie).get(mid)

        if not delete_rows:
            return "", 404

        db.session.delete(delete_rows)
        db.session.commit()

        return "", 204


# Вью класс для всех режиссеров
@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director)
        return directors_schema.dumps(all_directors.all()), 200


# Вью класс для режиссеров по id
@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did: int):
        director = db.session.query(Director).get(did)
        if not director:
            return "", 404
        return director_schema.dump(director), 200


# Вью класс для всех жанров
@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre).all()
        return genres_schema.dumps(all_genres), 200


# Вью класс для жанров по id
@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    def get(self, gid: int):
        genre = db.session.query(Genre).get(gid)
        if not genre:
            return "", 404
        return director_schema.dump(genre), 200


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
