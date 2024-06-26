from google.api_core.exceptions import GoogleAPIError

from utils.constants import PROJECT_ID, DATASET_ID, TABLES_KEYS
from utils.table_logger import setup_logger


class TableManager:

    def __init__(self, client, table, row):
        self.bq_client = client
        self.table = table
        self.row = row
        self.key_field = TABLES_KEYS[self.table]
        self.key_value = self.row[TABLES_KEYS[self.table]]

    def not_exist(self, key):
        table = f"{PROJECT_ID}.{DATASET_ID}.{self.table}"
        query = f"""SELECT COUNTIF({self.key_field} = {key}) AS record_count FROM `{table}`"""
        query_result = self.bq_client.query(query).result()
        record_count = next(query_result).get("record_count", 0)
        return record_count == 0

    def insert(self):
        table_ref = self.bq_client.dataset(DATASET_ID).table(self.table)
        tollway_logger = setup_logger(True)

        try:
            table_insert = self.bq_client.insert_rows_json(table_ref, [self.row])
            tollway_logger.info(f"Successfully inserted {self.key_field} {self.key_value} into BigQuery")
        except (GoogleAPIError, Exception) as e:
            tollway_logger.exception(
                f"Encountered errors while inserting {self.key_field} {self.key_value} into BigQuery: {e}"
            )
            raise

    def execute(self, perform_check):
        if perform_check:
            not_exist = self.not_exist(self.key_value)
            if not not_exist:
                return

        self.insert()
