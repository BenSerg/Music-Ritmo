from sqlmodel import SQLModel, Session, create_engine, Field, Relationship


DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# Таблицы связи "многие к многим"
class GenreTrack(SQLModel, table=True):
    __tablename__ = "Genre_Tracks"
    genre_id: int = Field(default=None, primary_key=True, foreign_key="Genres.id")
    track_id: int = Field(default=None, primary_key=True, foreign_key="Tracks.id")


class ArtistTrack(SQLModel, table=True):
    __tablename__ = "Artist_Tracks"
    artist_id: int = Field(default=None, primary_key=True, foreign_key="Artists.id")
    track_id:  int = Field(default=None, primary_key=True, foreign_key="Tracks.id")


class ArtistAlbum(SQLModel, table=True):
    __tablename__ = "Artist_Albums"
    artist_id: int = Field(default=None, primary_key=True, foreign_key="Artists.id")
    album_id:  int = Field(default=None, primary_key=True, foreign_key="Albums.id")


class TagTrack(SQLModel, table=True):
    __tablename__ = "Tag_Tracks"
    tag_id:   int = Field(default=None, primary_key=True, foreign_key="Tags.id")
    track_id: int = Field(default=None, primary_key=True, foreign_key="Tracks.id")


class PlaylistTrack(SQLModel, table=True):
    __tablename__ = "Playlist_Tracks"
    playlist_id: int = Field(default=None, primary_key=True, foreign_key="Playlists.id")
    track_id:    int = Field(default=None, primary_key=True, foreign_key="Tracks.id")
    added_at: str

    playlist: "Playlist" = Relationship(back_populates="playlist_tracks")
    track:    "Track"    = Relationship(back_populates="track_playlists")


class FavouriteTrack(SQLModel, table=True):
    __tablename__ = "Favourite_Tracks"
    user_id:  int = Field(default=None, primary_key=True, foreign_key="Users.id")
    track_id: int = Field(default=None, primary_key=True, foreign_key="Tracks.id")
    added_at: str

    user:  "User"  = Relationship(back_populates="favourite_tracks")
    track: "Track" = Relationship(back_populates="track_favourites")


class FavouriteAlbum(SQLModel, table=True):
    __tablename__ = "Favourite_Albums"
    user_id:  int = Field(default=None, primary_key=True, foreign_key="Users.id")
    album_id: int = Field(default=None, primary_key=True, foreign_key="Albums.id")
    added_at: str

    user:  "User"  = Relationship(back_populates="favourite_albums")
    album: "Album" = Relationship(back_populates="album_favourites")


class FavouritePlaylist(SQLModel, table=True):
    __tablename__ = "Favourite_Playlists"
    user_id:     int = Field(default=None, primary_key=True, foreign_key="Users.id")
    playlist_id: int = Field(default=None, primary_key=True, foreign_key="Playlists.id")
    added_at: str

    user:     "User"     = Relationship(back_populates="favourite_playlists")
    playlist: "Playlist" = Relationship(back_populates="playlist_favourites")


# Основные таблицы
class User(SQLModel, table=True):
    __tablename__ = "Users"
    id: int | None = Field(default=None, primary_key=True)
    login: str
    password: str
    avatar: str

    playlists: list["Playlist"] = Relationship(back_populates="user")
    favourite_tracks:    list["FavouriteTrack"]    = Relationship(back_populates="user")
    favourite_albums:    list["FavouriteAlbum"]    = Relationship(back_populates="user")
    favourite_playlists: list["FavouritePlaylist"] = Relationship(back_populates="user")


class Track(SQLModel, table=True):
    __tablename__ = "Tracks"
    id: int | None = Field(default=None, primary_key=True)
    file_path: str
    file_size: int
    type: str
    title: str = Field(index=True)
    album_id: int | None = Field(foreign_key="Albums.id")
    album_position: int | None
    year: str | None
    plays_count: int
    cover: bytes | None

    bit_rate: int
    bits_per_sample: int
    sample_rate: int
    channels: int
    duration: int

    album: "Album" = Relationship(back_populates="tracks")
    genres:  list["Genre"]  = Relationship(back_populates="tracks", link_model=GenreTrack)
    artists: list["Artist"] = Relationship(back_populates="tracks", link_model=ArtistTrack)
    tags:    list["Tag"]    = Relationship(back_populates="tracks", link_model=TagTrack)
    track_playlists:  list["PlaylistTrack"]  = Relationship(back_populates="track")
    track_favourites: list["FavouriteTrack"] = Relationship(back_populates="track")


class Artist(SQLModel, table=True):
    __tablename__ = "Artists"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    tracks: list["Track"] = Relationship(back_populates="artists", link_model=ArtistTrack)
    albums: list["Album"] = Relationship(back_populates="artists", link_model=ArtistAlbum)


class Album(SQLModel, table=True):
    __tablename__ = "Albums"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    total_tracks: int
    year: str | None
    cover: bytes | None

    tracks: list["Track"] = Relationship(back_populates="album")
    artists: list["Artist"] = Relationship(back_populates="albums", link_model=ArtistAlbum)
    album_favourites: list["FavouriteAlbum"] = Relationship(back_populates="album")


class Playlist(SQLModel, table=True):
    __tablename__ = "Playlists"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    user_id: int = Field(foreign_key="Users.id")
    total_tracks: int
    create_date: str

    user: "User" = Relationship(back_populates="playlists")
    playlist_tracks:     list["PlaylistTrack"]     = Relationship(back_populates="playlist")
    playlist_favourites: list["FavouritePlaylist"] = Relationship(back_populates="playlist")

class Genre(SQLModel, table=True):
    __tablename__ = "Genres"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    tracks: list["Track"] = Relationship(back_populates="genres", link_model=GenreTrack)


class Tag(SQLModel, table=True):
    __tablename__ = "Tags"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    tracks: list["Track"] = Relationship(back_populates="tags", link_model=TagTrack)
