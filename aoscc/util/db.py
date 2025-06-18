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


def fetch_all(table: str, cond: dict = None) -> list[dict]:
    cond = cond or {}
    return query_all(
        f'SELECT * FROM {table} WHERE {(
            " AND ".join(f"{k} = ?" for k in cond.keys())
        ) if cond else '1'}',
        tuple((cond or {}).values())
    )


def fetch_one(table: str, cond: dict = None) -> dict|None:
    if rows := fetch_all(table, cond):
        return rows[0]


def insert_dict(table: str, d: dict[str,str|int], commit: bool = True) -> int:
    cur = g.db.execute(  # Note: do not use INSERT OR REPLACE due to foreign key
        f'INSERT INTO {table}({",".join(d.keys())})'
        f' VALUES({",".join(["?"]*len(d))})'
        f' ON CONFLICT DO UPDATE SET'  # UPSERT clasue for "replacing"
        f' {",".join(f'{k}=excluded.{k}' for k in d.keys())}',
        tuple(d.values())
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
