import sqlite3
from pathlib import Path

from flask import g, current_app

from . import bp


@bp.before_app_request
def open_db():
    g.db = sqlite3.connect(Path(current_app.instance_path) / 'aoscc.sqlite')
    g.db.row_factory = sqlite3.Row
    g.db.execute('PRAGMA foreign_keys = ON')


@bp.teardown_app_request
def close_db(_):
    g.db.close()


def query_all(sql: str, args: tuple = ()) -> list[dict]:
    cur = g.db.execute(sql, args)
    rows = cur.fetchall()
    return list(map(dict, rows))


def fetch_all(table: str, cond: dict) -> list[dict]:
    return query_all(
        f'SELECT * FROM {table} WHERE {(
            " AND ".join(f"{k} = ?" for k in cond.keys())
        ) if cond else '1'}',
        tuple(cond.values())
    )


def fetch_one(table: str, cond: dict) -> dict|None:
    if rows := fetch_all(table, cond):
        return rows[0]


def insert_dict(table: str, d: dict[str,str|int], commit: bool = True) -> int:
    cur = g.db.execute(
        f'INSERT OR REPLACE INTO {table}({",".join(d.keys())}) VALUES({",".join(["?"]*len(d))})',
        tuple(d.values()),
    )
    if commit:
        g.db.commit()
    return cur.lastrowid


def delete_from(table: str, cond: dict) -> int:
    cur = g.db.execute(
        f'DELETE FROM {table} WHERE {" AND ".join(f"{k} = ?" for k in cond.keys())}',
        tuple(cond.values())
    )
    g.db.commit()
    return cur.rowcount
