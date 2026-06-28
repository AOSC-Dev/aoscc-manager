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


def _build_condition(cond: dict) -> tuple[str, tuple]:
    return (' AND '.join(f'`{k}` = ?' for k in cond.keys())) if cond else '1'


def fetch_all(table: str, cond: dict = None, limit: int = None) -> list[dict]:
    return query_all(
        f'SELECT * FROM {table} WHERE {_build_condition(cond)}'
        f'{f' LIMIT {limit}' if limit is not None else ''}',
        tuple((cond or {}).values())
    )


def count_rows(table: str, cond: dict = None) -> int:
    cur = g.db.execute(
        f'SELECT COUNT(*) FROM {table} WHERE {_build_condition(cond)}',
        tuple((cond or {}).values())
    )
    return cur.fetchone()[0]


def fetch_one(table: str, cond: dict = None) -> dict|None:
    if rows := fetch_all(table, cond, limit=1):
        return rows[0]


def insert_dict(table: str, d: dict[str,str|int], commit: bool = True) -> int:
    cur = g.db.execute(  # Note: do not use INSERT OR REPLACE due to foreign key
        f'INSERT INTO {table}(`{"`,`".join(d.keys())}`)'
        f' VALUES({",".join(["?"]*len(d))})'
        f' ON CONFLICT DO UPDATE SET'  # UPSERT clasue for "replacing"
        f' {",".join(f'`{k}`=excluded.`{k}`' for k in d.keys())}',
        tuple(d.values())
    )
    if commit:
        g.db.commit()
    return cur.lastrowid


def delete_from(table: str, cond: dict, commit: bool = True) -> int:
    cur = g.db.execute(
        f'DELETE FROM {table} WHERE {" AND ".join(f"`{k}` = ?" for k in cond.keys())}',
        tuple(cond.values())
    )
    if commit:
        g.db.commit()
    return cur.rowcount


def update_table(table: str, d: dict[str,str|int], cond: dict, commit: bool = True) -> int:
    cur = g.db.execute(
        f'UPDATE {table} SET {",".join(f"`{k}` = ?" for k in d.keys())} '
        f'WHERE {" AND ".join(f"`{k}` = ?" for k in cond.keys())}',
        tuple(d.values())+tuple(cond.values()),
    )
    if commit:
        g.db.commit()
    return cur.rowcount
