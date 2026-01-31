import os
import sys
import time

import psycopg2

from app.core.config import settings


def wait_for_db(database_url: str, timeout_seconds: int, interval_seconds: float) -> None:
    start_time = time.time()
    while True:
        try:
            connection = psycopg2.connect(database_url)
            connection.close()
            return
        except Exception as exc:
            if time.time() - start_time >= timeout_seconds:
                print(
                    f"数据库连接超时({timeout_seconds}s): {exc}",
                    file=sys.stderr,
                )
                raise
            time.sleep(interval_seconds)


def main() -> None:
    database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    timeout_seconds = int(os.getenv("DB_WAIT_TIMEOUT", "60"))
    interval_seconds = float(os.getenv("DB_WAIT_INTERVAL", "1"))
    wait_for_db(database_url, timeout_seconds, interval_seconds)


if __name__ == "__main__":
    main()
