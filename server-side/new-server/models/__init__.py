from orator import DatabaseManager, Model


config = {
    'sqlite': {
        'driver': 'sqlite',
        # 'host': 'localhost',
        'database': 'my_db',
        # 'user': 'root',
        # 'password': '',
        # 'prefix': ''
    }
}

db = DatabaseManager(config)
Model.set_connection(db)