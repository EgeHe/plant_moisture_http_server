from influxdb import InfluxDBClient


class DBClient:
    def __init__(self, host='localhost', port=8086):
        self._host = host
        self._port = port
        self._client = self._create_client()

    def _create_client(self):
        return InfluxDBClient(self._host, self._port)

    def get_databases(self):
        return [db['name'] for db in self._client.get_list_database()]

    def create_database(self, database):
        self._client.create_database(database)

    def switch_database(self, database):
        self._client.switch_database(database)

    def write_data_to_db(self, json_data):
        self._client.write_points(json_data)
