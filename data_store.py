from abc import ABC, abstractmethod
import pandas as pd
import json
import csv


class DataStore(ABC):
    @abstractmethod
    def save(self, data, filename):
        """Save data to a file or database."""
        pass

    @abstractmethod
    def load(self, filename):
        """Load data from a file or database."""
        pass


class JSONStore(DataStore):
    def save(self, data, filename):
        data.to_json(filename, orient='records', lines=True)

    def load(self, filename):
        return pd.read_json(filename, orient='records', lines=True)


class CSVStore(DataStore):
    def save(self, data, filename):
        data.to_csv(filename, index=False)

    def load(self, filename):
        return pd.read_csv(filename)


# Assuming you will later implement a PostgreSQL store
# class PostgresStore(DataStore):
#     def save(self, data, table_name, connection_params):
#         data.to_sql(table_name, con=connection_params, if_exists='replace', index=False)
#
#     def load(self, table_name, connection_params):
#         return pd.read_sql_table(table_name, con=connection_params)

# Example usage
if __name__ == "__main__":
    data = pd.DataFrame({
        'date': ['2021-01-01', '2021-01-02'],
        'event': ['New Year Party', 'Strategy Meeting'],
        'location': ['New York', 'London']
    })

    # Initialize a JSON store and save data
    json_store = JSONStore()
    json_store.save(data, 'events.json')

    # Load data back into a DataFrame
    loaded_data = json_store.load('events.json')
    print(loaded_data)
