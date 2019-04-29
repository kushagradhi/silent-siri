import sqlite3

class DBInterface:
    paths = {'geo': '..//data//WorldGeography.sqlite',
              'movie': '..//data//oscar-movie_imdb.sqlite',
              'music': '..//data//music.sqlite'}


    def __init__(self):
        self.connections = {}
        self.cursors = {}

    def createConnections(self):
        for category in self.paths:
            self.connections[category] = sqlite3.connect(self.paths[category])
        # print(self.connections)
        # conn_movie = sqlite3.connect(pathMovieDB)
        # conn_music = sqlite3.connect(pathMusicDB)
        # conn_geo   = sqlite3.connect(pathGeoDB)

    def createCursors(self):
        for category in self.paths:
            self.cursors[category] = self.connections[category].cursor()
        # print(self.cursors)
        # cursor_movie = conn_movie.cursor()
        # cursor_music = conn_music.cursor()
        # cursor_geo = conn_geo.cursor()

    def start(self):
        if not self.connections:
            self.createConnections()
            self.createCursors()

    def executeQuery(self, query, category):
        return self.cursors[category].execute(query).fetchall()
    # print(conn_movie.execute('''select * from OSCAR limit 5;''').fetchall())

    def closeConnections(self):
        for category in self.paths:
            self.connections[category].close()
        # conn_music.close()
        # conn_geo.close()


# t=DBInterface()
# t.start()
# print(t.executeQuery('select * from actor limit 1', 'movie'))
# t.closeConnections()