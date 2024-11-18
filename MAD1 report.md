# Grocery Store V1 Web App Report

## Author:
- **Name** - 
- **Roll** - roll
- **emailid** - student emailID
- **About:** Hey there! this is Arvind, a 26 year old Web Analyst specializing in Google Analytics, Adobe Analytics, Adobe Launch and Google Tag Manager. I am also an undergrad student at IIT Madras BS Degree (Programming and Data Science).

## Description
The Music Streaming Web App is a web-based application designed to display songs, artist and can play songs. User can perform **creation**, **deletion**, and **deletion** of contents, songs by the Admin. The purpose of this report is to provide an overview of the app, including its features, functionality, and potential areas for improvement.

## Frameworks used in the project
- ***Flask***:- for backend of the application
- ***Flask: Session***:- for implementing session for authentication and authorization.
- ***Jinja2***:- For templates
- ***CSS***:- For styling

## Tools and Technologies
These are tools and technologies to develop Music Streaming Web App. These include:

- *** CSS***:- for styling and aesthetics of the application
- ***requests***:- Requests is a popular Python library used for making HTTP requests to APIs, websites, and other web services.
- ***os***:- for some operation related with files directory in the application
- ***session***:- Flask extension supports Server-side session to our application.
- ***redirect***:-used to redirect a user to another endpoint using a specified URL and assign a specified
status code.
- ***request***:- used to handle HTTP requests and responses.
- ***render_template***:- used to render html templates based on the Jinja2 engine that is found in the
application's templates folder.
- ***sqlite3 python module***:- used to create database schema and tables using SQLAlchemy with Flask by
providing defaults and helpers.

## Database Schema
1. ***Relations:*** There are ten tables in the database namely User, Creator, Owner, Playlist , PlaylistSong, Song, Album, Like, Comment, FlaggedContent. There are foreign keys to map tables like song with albums, playlistsong with playlist etc. 
2. ***Foreign Keys :***
-  Table Playlist - FOREIGN KEY (user_id)  REFERENCES User(id),
                    FOREIGN KEY (creator_id) REFERENCES Creator(id)

- Table PlaylistSong - FOREIGN KEY (playlist_id) REFERENCES Playlist(playlist_id),
                       FOREIGN KEY (song_id) REFERENCES Song(song_id)

- Table Song - FOREIGN KEY (creator_id) REFERENCES Creator(creator_id),
               FOREIGN KEY (album_id) REFERENCES Album(album_id)

- Table Album - FOREIGN KEY (creator_id) REFERENCES Creator(creator_id)

- Table Like - FOREIGN KEY (user_id) REFERENCES User(user_id),
               FOREIGN KEY (creator_id) REFERENCES Creator(creator_id),
               FOREIGN KEY (song_id) REFERENCES Song(song_id)

- Table Comment - FOREIGN KEY (user_id) REFERENCES User(user_id),
                  FOREIGN KEY (song_id) REFERENCES Song(song_id)

- Table FlaggedContent - FOREIGN KEY (song_id) REFERENCES Song(song_id),
                         FOREIGN KEY (creator_id) REFERENCES Creator(id)


## Architecture and Features:
The project code is organised based on its utility in different files. I have named my project Musicapp-1.
Inside this folder there one module with name flaskr this is the flask app object or the root app, and there one more folder with name instance having the sqlite database file. I side the module flaskr I am having all the python files for controllers, database, config etc. And the templates, static folder. 
Report folder with the report.pdf file, demo video and file to setup and run this project on windows.

## Routers used in admin.py
- @bp.route('/users')
- @bp.route('/creators')
- @bp.route('/albums')
- @bp.route('/songs')
- @bp.route('/flags')
- @bp.route('/remove/flag/<int:id>', methods=('GET', 'POST'))
- @bp.route('/report/content/<int:id>', methods=('GET', 'POST'))
- @bp.route('/report/content/<int:id>', methods=('GET', 'POST'))


## Routers used in album.py
- @bp.route('/album')
- @bp.route('/<int:id>/songs/album')
- @bp.route('/create/album', methods=('GET', 'POST'))
- @bp.route('/<int:id>/update/album', methods=('GET', 'POST'))
- @bp.route('/<int:id>/delete_album', methods=('GET', 'POST'))


## Routers used in auth.py
- @bp.route('/register', methods=('GET', 'POST'))
- @bp.route('/creator', methods=('GET', 'POST'))
- @bp.route('/switch/to/creator')
- @bp.route('/creator/block/<int:id>')
- @bp.route('/creator/unblock/<int:id>')
- @bp.route('/user/remove/<int:id>')
- @bp.route('/user/block/<int:id>')
- @bp.route('/user/unblock/<int:id>')
- @bp.route('/login', methods=('GET', 'POST'))
- @bp.route('/admin/login', methods=('GET', 'POST'))
- @bp.before_app_request
- @bp.route('/logout')

## Routers used in playlist.py
- @bp.route('/playlist')
- @bp.route('/<int:id>/songs/playlist')
- @bp.route('/songs/<int:song_id>/add/here/<int:playlist_id>')
- @bp.route('/songs/<int:song_id>/remove/from/<int:playlist_id>')
- @bp.route('/create/playlist', methods=('GET', 'POST'))
- @bp.route('/<int:id>/update/playlist', methods=('GET', 'POST'))
- @bp.route('/<int:id>/delete/playlist', methods=('POST',))

## Routers used in song.py
- @bp.route('/')
- @bp.route('/create', methods=('GET', 'POST'))
- @bp.route('/current/song/<int:song_id>')
- @bp.route('/play/<int:song_id>')
- @bp.route('/<int:id>/update', methods=('GET', 'POST'))
- @bp.route('/<int:id>/delete', methods=('GET', 'POST'))
- @bp.route('/<int:id>/like')
- @bp.route('/<int:id>/add/to/playlist', methods=('GET',))

A short demo video link is here [ https://drive.google.com/file/d/1bQhFJ5e-fk1m4aAx1Zsz_u-bHUDKRHZW/view?usp=sharing ]().