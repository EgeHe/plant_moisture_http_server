import cherrypy
import datetime
from plant_moisture_http_server.db_client import DBClient


@cherrypy.expose
class DataServer:

    STATION = 'station'
    MIN_MOIST = 'min_moist'
    MAX_MOIST = 'max_moist'
    MOISTURE = 'moisture'
    DB_NAME = 'plant_moisture_db'
    MEASUREMENT = 'plant_moisture'

    def __init__(self):
        self.db_client = DBClient(host='192.168.1.199', port=8086)
        if self.DB_NAME not in self.db_client.get_databases():
            self.db_client.create_database(self.DB_NAME)
        self.db_client.switch_database(self.DB_NAME)

        self.station_limits = {
            '1': {self.MIN_MOIST: 1024.0, self.MAX_MOIST: 0.0}
        }

    def GET(self, **kwargs):
        if self.STATION in kwargs.keys() and self.MOISTURE in kwargs.keys():
            station = kwargs[self.STATION]
            moisture = kwargs[self.MOISTURE]
            self._write_entry_to_db(station, moisture)

    def POST(self, **kwargs):

        if self.STATION not in kwargs.keys():
            return
        station = kwargs[self.STATION]

        if self.MAX_MOIST in kwargs.keys():
            self._set_station_max(station, kwargs[self.MAX_MOIST])

        if self.MIN_MOIST in kwargs.keys():
            self._set_station_min(station, kwargs[self.MIN_MOIST])

        if self.MOISTURE in kwargs.keys():
            raw_moisture = kwargs[self.MOISTURE]
            self._write_entry_to_db(station, self._handle_moisture(raw_moisture, station))

    def _set_station_min(self, station, value):
        pass

    def _set_station_max(self, station, value):
        pass

    def _handle_moisture(self, raw_moisture, station):
        try:
            station_limits = self.station_limits[station]
            min_moist = station_limits[self.MIN_MOIST]
            max_moist = station_limits[self.MAX_MOIST]
        except KeyError:
            min_moist = 1024.0
            max_moist = 0.0

        moist = raw_moisture - min_moist
        relative_moist = moist / (max_moist - min_moist)

        return int(relative_moist * 100.0)

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
