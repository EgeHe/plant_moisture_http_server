import cherrypy
import datetime
from plant_moisture_http_server.db_client import DBClient


@cherrypy.expose
class DataServer:

    STATION = 'station'
    MOISTURE = 'moisture'
    DB_NAME = 'plant_moisture_db'
    MEASUREMENT = 'plant_moisture'

    def __init__(self):
        self.db_client = DBClient(host='192.168.1.199', port=8086)
        if self.DB_NAME not in self.db_client.get_databases():
            self.db_client.create_database(self.DB_NAME)
        self.db_client.switch_database(self.DB_NAME)

    def GET(self, **kwargs):
        if self.STATION in kwargs.keys() and self.MOISTURE in kwargs.keys():
            station = kwargs[self.STATION]
            moisture = kwargs[self.MOISTURE]
            self._write_entry_to_db(station, moisture)

    def POST(self, **kwargs):
        if self.STATION in kwargs.keys() and self.MOISTURE in kwargs.keys():
            station = kwargs[self.STATION]
            raw_moisture = kwargs[self.MOISTURE]
            self._write_entry_to_db(station, self._handle_moisture(raw_moisture))

    def _handle_moisture(self, raw_moisture):
        return raw_moisture

    def _write_entry_to_db(self, station, moisture):
        json_data = [
            {
                "measurement": self.MEASUREMENT,
                "tags": {
                    self.STATION: str(station),
                },
                "time": self._get_time(),
                "fields": {
                    self.MOISTURE: int(moisture)
                }
            }
        ]
        self.db_client.write_data_to_db(json_data)

    @classmethod
    def _get_time(cls):
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def start():
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')]
        },
        'global': {'server.socket_host': '0.0.0.0'}
    }
    server = DataServer()
    cherrypy.quickstart(server, '/', conf)
