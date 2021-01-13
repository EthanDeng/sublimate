import sqlite3
from sqlalchemy import create_engine
import pandas as pd

def read_pg(query_sql):
	db_string = "..."
	pg_conn = create_engine(db_string)
	data = pd.read_sql(query_sql, pg_conn)
	return data


def dump_sqlite(df, db, table, mode):
	db = db + '.db' if not db.endswith('.db') else db
	conn = sqlite3.connect(db)
	df.to_sql(table, conn, if_exists=mode, index=False)
	conn.close()

def query_sqlite(db, table):
	conn = sqlite3.connect(db)
	data = pd.read_sql_query("SELECT * FROM %s" % table, conn)
	conn.close()
	return data
