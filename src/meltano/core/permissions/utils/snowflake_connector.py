import logging
import os

from typing import Dict, List
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL


# Don't show all the info log messages from Snowflake
for logger_name in ["snowflake.connector", "botocore", "boto3"]:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.WARNING)


class SnowflakeConnector:
    def __init__(self, config: Dict = None) -> None:
        if not config:
            config = {
                "user": os.getenv("SNOWFLAKE_PERMISSIONS_USER"),
                "password": os.getenv("SNOWFLAKE_PERMISSIONS_PASSWORD"),
                "account": os.getenv("SNOWFLAKE_PERMISSIONS_ACCOUNT"),
                "database": os.getenv("SNOWFLAKE_PERMISSIONS_DATABASE"),
                "role": os.getenv("SNOWFLAKE_PERMISSIONS_ROLE"),
                "warehouse": os.getenv("SNOWFLAKE_PERMISSIONS_WAREHOUSE"),
            }

        self.engine = create_engine(
            URL(
                user=config["user"],
                password=config["password"],
                account=config["account"],
                database=config["database"],
                role=config["role"],
                warehouse=config["warehouse"],
            )
        )

    def show_query(self, entity) -> List[str]:
        names = []

        query = f"SHOW {entity}"
        with self.engine.connect() as connection:
            results = connection.execute(query).fetchall()

            for result in results:
                names.append(result["name"].upper())

        return names

    def show_databases(self) -> List[str]:
        return self.show_query("DATABASES")

    def show_warehouses(self) -> List[str]:
        return self.show_query("WAREHOUSES")

    def show_roles(self) -> List[str]:
        return self.show_query("ROLES")

    def show_users(self) -> List[str]:
        return self.show_query("USERS")

    def show_schemas(self, database: str = None) -> List[str]:
        names = []

        if database:
            query = f"SHOW TERSE SCHEMAS IN DATABASE {database}"
        else:
            query = f"SHOW TERSE SCHEMAS IN ACCOUNT"

        with self.engine.connect() as connection:
            results = connection.execute(query).fetchall()

            for result in results:
                names.append(
                    f"{result['database_name'].upper()}.{result['name'].upper()}"
                )

        return names

    def show_tables(self) -> List[str]:
        names = []

        query = f"SHOW TERSE TABLES IN ACCOUNT"
        with self.engine.connect() as connection:
            results = connection.execute(query).fetchall()

            for result in results:
                names.append(
                    f"{result['database_name'].upper()}"
                    + f".{result['schema_name'].upper()}"
                    + f".{result['name'].upper()}"
                )

        return names
