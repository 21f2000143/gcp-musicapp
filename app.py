from flask import Flask, Blueprint, render_template, request, abort, jsonify, redirect, url_for, flash, make_response
from database import *
from datetime import datetime
import base64
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from functools import wraps
from flask import request
from sqlalchemy import or_

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user is None or current_user.role != role:
                return render_template('index.html')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.sqlite3'
db.init_app(app)
app.app_context().push()
with app.app_context():
    db.create_all()
exist_admin=User.query.filter_by(username="aastha@123").first()
if not exist_admin:
    the_admin = User(username="aastha@123", password=generate_password_hash("password",method='scrypt'), role="admin", isblocked=0)
    db.session.add(the_admin)
    db.session.commit()

#---------------------- All operational endpoints --------------#
admin = Blueprint('admin', __name__)

def get_chart_data():
    user_count = User.query.filter_by(role='user').count()
    creator_count = User.query.filter_by(role='creator').count()
    album_count = Album.query.count()
    song_count = Song.query.count()
    data = {
        'labels': ['Users', 'Creators', 'Albums', 'Songs'],
        'datasets': [{
            'label': 'Click',
            'data': [user_count, creator_count, album_count, song_count],
            'backgroundColor': ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)', 'rgba(150, 106, 86, 0.2)'],
            'borderColor': ['rgba(255,99,132,1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)', 'rgba(150, 106, 86, 0.2)'],
            'borderWidth': 1
        }]
    }
    return jsonify(data)

@admin.route('/chart-data')
def chart_data():
    return get_chart_data()

@admin.route('/admin-chart')
def admin_chart():
    return render_template('admin/adminchart.html')

@admin.route('/users')
def index_users():
    search = request.args.get('search')
    users=None
    if search is None:
        users = User.query.filter(User.role == 'user').all()
    else:
        users = User.query.filter(User.username.ilike(f'%{search}%'), User.role == 'user').all()   
    return render_template('admin/user.html', users=users)

@admin.route('/creators')
def index_creators():
    search = request.args.get('search')
    creators=None
    if not search:
        creators = User.query.filter(User.role == 'creator').all()
    else:
        creators = User.query.filter(User.username.ilike(f'%{search}%'), User.role == 'creator').all()   
    return render_template('admin/creator.html', creators=creators)

@admin.route('/songs')
def index_songs():
    search = request.args.get('search')
    songs=None
    if search is None:
        songs = Song.query.order_by(Song.created.desc()).all()
    else:
        songs = Song.query.filter(Song.title.ilike(f'%{search}%')).order_by(Song.created.desc()).all() 
    return render_template('admin/song.html', songs=songs)

@admin.route('/flags')
def index_flags():
    search = request.args.get('search')
    flags=None  
    if search:
        flags = FlaggedContent.query.filter(FlaggedContent.reason.ilike(f'%{search}%')).all()
    else:            
        flags = FlaggedContent.query.all()
    return render_template('admin/flags.html', flags=flags)


@admin.route('/remove/flag/<int:id>', methods=('GET', 'POST'))
@login_required
def remove_flag(id):
    flag = FlaggedContent.query.filter_by(flag_id=id).first()
    if flag:
        db.session.delete(flag)
        db.session.commit()
        flash('Deleted successfully.')
        return redirect(url_for('song.index'))
    else:
        flash('Not found.')
        return redirect(url_for('song.index'))

@admin.route('/report/content/<int:id>', methods=('GET', 'POST'))
@login_required
def report_content(id):
    if request.method == 'POST':
        title = request.form['title']
        reason = request.form['reason']
        error = None

        if not title:
            error = 'Title is required.'
        if not reason:
            error = 'Reason is required.'

        if error is not None:
            flash(error)
        else:
            flag = FlaggedContent(song_id=id, type="content", reason=reason)
            db.session.add(flag)
            db.session.commit()
            flash('Reported successfully.')
            return redirect(url_for('song.index'))

    return render_template('admin/report_content.html', id=id)

@admin.route('/report/creator/<int:id>', methods=('GET', 'POST'))
@login_required
def report_creator(id):
    if request.method == 'POST':
        title = request.form['title']
        reason = request.form['reason']
        error = None

        if not title:
            error = 'Title is required.'
        if not reason:
            error = 'Reason is required.'

        if error is not None:
            flash(error)
        else:
            flag = FlaggedContent(creator_id=id, type="creator", reason=reason)
            db.session.add(flag)
            db.session.commit()
            flash('updated album')
            return redirect(url_for('song.index'))
    return render_template('admin/report_creator.html', id=id)

#-------------------authentication and authorization-----------------#
album = Blueprint('album', __name__)

@album.route('/album')
def index_album():
    search_word=request.args.get('search')
    albums=None
    if search_word:
        albums = Album.query.filter(Album.title.ilike(f'%{search_word}%')).all()
    else:
        albums = Album.query.order_by(Album.created.desc()).all()
    return render_template('album/index.html', albums=albums)

def get_album(id):
    album = Album.query.filter_by(album_id=id).first()
    if album is None:
        abort(404, f"Album id {id} doesn't exist.")
    return album

@admin.route('/albums')
def index_albums():
    search = request.args.get('search')
    albums=None
    if search:
        albums = Album.query.filter(Album.title.ilike(f'%{search}%')).all()
    else:
        albums = Album.query.order_by(Album.created.desc()).all()
    albums_data = [{
            'title': album.title,
            'album_id': album.album_id,
            'created': album.created,
            'username': album.creator.username,
            'creator_id': album.creator_id
        } for album in albums ]
    return render_template('admin/album.html', albums=albums_data)

@album.route('/<int:id>/songs/album')
def songs_album(id):
    album = get_album(id)
    album=Album.query.filter_by(album_id=id).first()
    songs = Song.query.filter_by(album_id=id).all()
    return render_template('song/index.html', songs=songs, album=album)

@album.route('/create/album', methods=('GET', 'POST'))
@login_required
def create_album():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        error = None

        if not title:
            error = 'Title is required.'
        if not genre:
            error = 'genre is required.'

        if error is not None:
            flash(error)
        else:
            new_album = Album(title=title, genre=genre, creator_id=current_user.id)
            db.session.add(new_album)
            db.session.commit()
            flash('album added.')
            return redirect(url_for('song.index'))
    return render_template('album/create.html')

@album.route('/<int:id>/update/album', methods=('GET', 'POST'))
@login_required
def update_album(id):
    album = get_album(id)
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        error = None

        if not title:
            error = 'Title is required.'
        if not genre:
            error = 'Genre is required.'

        if error is not None:
            flash(error)
        else:
            album.title = title
            album.genre = genre
            db.session.commit()
            flash('updated album')
            return redirect(url_for('song.index'))

    return render_template('album/update.html', album=album)

@album.route('/<int:id>/delete_album', methods=('GET', 'POST'))
@login_required
def delete_album(id):
    get_album(id)
    songs = Song.query.filter_by(album_id=id).all()
    for song in songs:
        likes = Like.query.filter_by(song_id=song.song_id).all()
        for like in likes:
            db.session.delete(like)
            db.session.commit()
        flags = FlaggedContent.query.filter_by(song_id=song.song_id).all()
        for flag in flags:
            db.session.delete(flag)
            db.session.commit()
        playlistsongs = PlaylistSong.query.filter_by(song_id=song.song_id).all()
        for playlistsong in playlistsongs:
            db.session.delete(playlistsong)
            db.session.commit()
        db.session.delete(song)
        db.session.commit()
    album = Album.query.filter_by(album_id=id).first()
    db.session.delete(album)
    db.session.commit()
    flash('deleted album and all songs in the album.')
    return redirect(url_for('song.index'))


#-------------------authentication and authorization-----------------#
playlist = Blueprint('playlist', __name__)

def get_playlist(id):
    playlist = Playlist.query.filter_by(playlist_id=id).first()
    if playlist is None:
        abort(404, f"playlist id {id} doesn't exist.")
    return playlist

@playlist.route('/playlist')
@login_required
def index_playlist():
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template('playlist/index.html', playlists=playlists)

@playlist.route('/<int:id>/songs/playlist')
@login_required
def songs_playlist(id):
    playlist = get_playlist(id)
    songs = playlist.playlist_songs
    return render_template('song/index.html', songs=songs, playlist=playlist)

@playlist.route('/songs/<int:song_id>/add/here/<int:playlist_id>')
@login_required
def add_here(song_id, playlist_id):
    already_added = PlaylistSong.query.filter_by(
        song_id=song_id,
        playlist_id=playlist_id
    ).first()
    if not already_added:
        playlist_song = PlaylistSong(song_id=song_id, playlist_id=playlist_id)
        db.session.add(playlist_song)
        db.session.commit()
        flash("song added into your playlist.")
        return redirect(url_for('song.index'))
    else:
        flash('Song is already added.')
        return redirect(url_for('song.add_to_playlist', id=song_id))

@playlist.route('/songs/<int:song_id>/remove/from/<int:playlist_id>')
@login_required
def remove_from(song_id, playlist_id):
    playlist_song = PlaylistSong.query.filter_by(song_id=song_id, playlist_id=playlist_id).first()
    db.session.delete(playlist_song)
    db.session.commit()
    flash("removed the song.")
    return redirect(url_for('playlist.songs_playlist', id=playlist_id))

@playlist.route('/create/playlist', methods=('GET', 'POST'))
@login_required
def create_playlist():
    if request.method == 'POST':
        title = request.form['title']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            new_playlist = Playlist(title=title, user_id=current_user.id)
            db.session.add(new_playlist)
            db.session.commit()
            flash('added playlist.')
            return redirect(url_for('playlist.index_playlist'))
    return render_template('playlist/create.html')


@playlist.route('/<int:id>/update/playlist', methods=('GET', 'POST'))
@login_required
def update_playlist(id):
    playlist = get_playlist(id)
    if request.method == 'POST':
        title = request.form['title']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            playlist.title = title
            db.session.commit()
            flash('updated playlist')
            return redirect(url_for('playlist.index_playlist'))

    return render_template('playlist/update.html', playlist=playlist)

@playlist.route('/<int:id>/delete/playlist', methods=('POST',))
@login_required
def delete_playlist(id):
    playlist_songs = PlaylistSong.query.filter_by(playlist_id=id).all()
    for playlist_song in playlist_songs:
        db.session.delete(playlist_song)
        db.session.commit()
    playlist = Playlist.query.filter_by(playlist_id=id).first()
    db.session.delete(playlist)
    db.session.commit()
    flash('deleted playlist.')
    return redirect(url_for('song.index'))

song = Blueprint('song', __name__)
def get_song(id):
    song = Song.query.filter_by(song_id=id).first()
    if song is None:
        abort(404, f"Song id {id} doesn't exist.")
    return song

@song.route('/')
def index():
    search_word=request.args.get('search') #url_for(' song.index')
    songs=None
    if search_word:
        songs = Song.query.filter(or_(
            Song.title.ilike(f'%{search_word}%'),
            Song.lyrics.ilike(f'%{search_word}%'),
            Song.creator.has(User.username.ilike(f'%{search_word}%')),
            Song.album.has(Album.genre.ilike(f'%{search_word}%'))
        )).all()
    else:
        songs = Song.query.order_by(Song.created.desc()).all()
    return render_template('song/index.html', songs=songs)

@song.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        audio_file = request.files['audio_file']
        if audio_file:
            audio_data = audio_file.read()
            audio_type = audio_file.filename.split('.')[-1]  # Extract the file extension
        lyrics = request.form.get('lyrics')
        album_id = request.form.get('album_id')
        error = None

        if not title:
            error = 'Title is required.'
        if not audio_file:
            error = 'audio_file is required.'
        if not album_id:
            error = 'album_id is required.'

        if error is not None:
            flash(error)
        else:
            if lyrics:
                new_song = Song(title=title, audio_data=audio_data, audio_type=audio_type, creator_id=current_user.id, username=current_user.username, album_id=album_id, lyrics=lyrics)
                db.session.add(new_song)
                db.session.commit()
            else:
                new_song = Song(title=title, audio_data=audio_data, audio_type=audio_type, creator_id=current_user.id, username=current_user.username, album_id=album_id)
                db.session.add(new_song)
                db.session.commit()
            return redirect(url_for('song.index'))
    albums = Album.query.all()
    return render_template('song/create.html', albums=albums)

@song.route('/current/song/<int:song_id>')
def current_song(song_id):
    like=None
    song = Song.query.filter_by(song_id=song_id).first()
    like=None
    if current_user.is_authenticated:
        like = Like.query.filter_by(song_id=song_id, user_id=current_user.id).first()
    return render_template('song/current_song.html', song=song, like=like)

@song.route('/play/<int:song_id>')
def play_audio(song_id):
    audio_data, audio_type=Song.query.filter_by(song_id=song_id).first().audio_data, Song.query.filter_by(song_id=song_id).first().audio_type
    response = make_response(audio_data)
    response.headers['Content-Type'] = f'audio/{audio_type}'
    return response

@song.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    song = get_song(id)
    if request.method == 'POST':
        title = request.form['title']
        audio_file = request.files['audio_file']
        if audio_file:
            audio_data = audio_file.read()
            audio_type = audio_file.filename.split('.')[-1]  # Extract the file extension
        lyrics = request.form.get('lyrics')
        album_id = request.form.get('album_id')
        error = None

        if not title:
            error = 'Title is required.'
        if not audio_file:
            error = 'audio_file is required.'
        if not album_id:
            error = 'album_id is required.'

        if error is not None:
            flash(error)
        else:
            if lyrics:
                song.album_id = album_id
                song.title = title
                song.audio_data = audio_data
                song.audio_type = audio_type
                song.lyrics = lyrics
                db.session.commit()
            else:
                song.album_id = album_id
                song.title = title
                song.audio_data = audio_data 
                song.audio_type = audio_type
                db.session.commit()
            flash('song updated')
            return redirect(url_for('song.index'))
    albums = Album.query.all()
    return render_template('song/update.html', song=song, albums=albums)

@song.route('/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):
    flags = FlaggedContent.query.filter_by(song_id=id).all()
    for flag in flags:
        db.session.delete(flag)
        db.session.commit()
    playlist_songs = PlaylistSong.query.filter_by(song_id=id).all()
    for playlistsong in playlist_songs:
        db.session.delete(playlistsong)
        db.session.commit()
    likes = Like.query.filter_by(song_id=id).all()
    for like in likes:
        db.session.delete(like)
        db.session.commit()
    song = Song.query.filter_by(song_id=id).first()
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for('song.index'))

@song.route('/<int:id>/like')
@login_required
def like(id):
    get_song(id)
    new_like = Like(song_id=id, user_id=current_user.id)
    db.session.add(new_like)
    db.session.commit()
    flash("you liked this song")
    return redirect(url_for('song.current_song', song_id=id))

@song.route('/<int:id>/add/to/playlist', methods=('GET',))
@login_required
def add_to_playlist(id):
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    song = Song.query.filter_by(song_id=id).first()
    return render_template('song/addtoplaylist.html', playlists=playlists, song=song)


#-------------------authentication and authorization-----------------#
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = User.query.filter_by(username=username).first()
        if user :
            if user.isblocked==1:
                error = 'You have been blocked.'
            elif check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('song.index'))
            else:
                error = 'Incorrect password.'
        else:
            error = 'Incorrect username.'
        flash(error)
    return render_template('auth/login.html')

@auth.route('/admin/login', methods=('GET', 'POST'))
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        owner = User.query.filter_by(username=username).first()
        if owner :
            if check_password_hash(owner.password, password):
                login_user(owner)
                return redirect(url_for('song.index'))
            else:
                error = 'Incorrect password.'
        else:
            error = 'Incorrect username.'
        flash(error)
    return render_template('admin/login.html')
    
@auth.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        if error is None:
            try:
                user = User.query.filter_by(username=username).first()
                if user:
                    raise db.IntegrityError
                user = User(username=username, password=generate_password_hash(password), role='user', isblocked=0)
                db.session.add(user)
                db.session.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        flash(error)
    return render_template('auth/register.html')

@auth.route('/switch/to/creator')
def switch_creator():
    error = None
    try:
        user = User.query.filter_by(id=current_user.id).first()
        user.role='creator'
        db.session.commit()
        error='You are now creator, login with same username and password'
    except db.IntegrityError:
        error = f"Something went wrong."
    flash(error)
    return redirect(url_for("song.index"))

@auth.route('/creator/block/<int:id>')
def creator_block(id):
    user = User.query.filter_by(id=id).first()
    if user:
        user.isblocked=1
        db.session.commit()
        flash("blocked the user")
        return redirect(url_for('admin.index_users'))
    abort(404)
 
@auth.route('/creator', methods=('GET', 'POST'))
def creator():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                user = User.query.filter_by(username=username).first()
                if user:
                    raise db.IntegrityError
                user = User(username=username, password=generate_password_hash(password), role='creator', isblocked=0)
                db.session.add(user)
                db.session.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        flash(error)
    return render_template('auth/creator.html')

@auth.route('/creator/unblock/<int:id>')
def creator_unblock(id):
    user = User.query.filter_by(id=id).first()
    if user:
        user.isblocked=0
        db.session.commit()
        flash("unblocked the user")
        return redirect(url_for('admin.index_users'))
    abort(404)    

@auth.route('/user/remove/<int:id>')
def user_remove(id):
    user = User.query.filter_by(id=id).first()
    if user:
        playlists = Playlist.query.filter_by(user_id=id).all()  
        for playlist in playlists:
            db.session.delete(playlist)
            db.commit()
        likes = Like.query.filter_by(user_id=id).all()  
        for like in likes:
            db.session.delete(playlist)
            db.commit()
    db.session.delete(user)
    db.session.commit()
    flash("removed the user")
    return redirect(url_for('admin.index_users'))

@auth.route('/user/block/<int:id>')
def user_block(id):
    user = User.query.filter_by(id=id).first()
    user.isblocked=1
    db.commit()
    flash("blocked the user")
    return redirect(url_for('admin.index_users'))

@auth.route('/user/unblock/<int:id>')
def user_unblock(id):
    user = User.query.filter_by(id=id).first()
    user.isblocked=0
    db.commit()
    db.commit()
    flash("unblocked the user")
    return redirect(url_for('admin.index_users'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('song.index'))


@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404


app.register_blueprint(auth)
app.register_blueprint(song)
app.register_blueprint(admin)
app.register_blueprint(album)
app.register_blueprint(playlist)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.filter_by(id=int(user_id)).first()

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)
