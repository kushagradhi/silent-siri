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

    def createCursors(self):
        for category in self.paths:
            self.cursors[category] = self.connections[category].cursor()

    def start(self):
        if not self.connections:
            self.createConnections()
            self.createCursors()

    def executeQuery(self, query, category):
        try:
            return self.cursors[category].execute(query).fetchall()
        except sqlite3.OperationalError as opError:
            return -1

    def closeConnections(self):
        for category in self.paths:
            self.connections[category].close()


# t=DBInterface()
# t.start()
# print(t.executeQuery('select * from actor limit 1', 'movie'))
# t.closeConnections()