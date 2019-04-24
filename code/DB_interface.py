import sqlite3

conn_movie = sqlite3.connect('../data//oscar-movie_imdb.sqlite')
# conn_music = sqlite3.connect('../data//music.sqlite')
# conn_geo   = sqlite3.connect('../data//WorldGeography.sqlite')

cursor_movie = conn_movie.cursor()
# cursor_music = conn_music.cursor()
# cursor_geo = conn_geo.cursor()
print(conn_movie.execute('''select * from Oscar limit 5;''').fetchall())

conn_movie.close()
# conn_music.close()
# conn_geo.close()