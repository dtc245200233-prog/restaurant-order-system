import os
import psycopg

def main():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        print("LỖI: Chưa thiết lập DATABASE_URL")
        raise SystemExit(1)

    try:
        with psycopg.connect(database_url, connect_timeout=5) as conn:
            result = conn.execute("SELECT current_database(), current_user").fetchone()
            print(f"Kết nối PostgreSQL thành công: database={result[0]}, user={result[1]}")
    except Exception as exc:
        print(f"Kết nối PostgreSQL thất bại: {exc}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
