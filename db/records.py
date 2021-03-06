from sqlalchemy import delete, select
from sqlalchemy.inspection import inspect


def _get_primary_key_column(table):
    primary_key_list = list(inspect(table).primary_key)
    # We do not support getting by composite primary keys
    assert len(primary_key_list) == 1
    return primary_key_list[0]


def get_record(table, engine, id_value):
    primary_key_column = _get_primary_key_column(table)
    query = select(table).where(primary_key_column == id_value)
    with engine.begin() as conn:
        result = conn.execute(query).fetchall()
        assert len(result) <= 1
        return result[0] if result else None


def get_records(table, engine, limit=None, offset=None):
    query = select(table).limit(limit).offset(offset)
    with engine.begin() as conn:
        return conn.execute(query).fetchall()


def create_record_or_records(table, engine, record_data):
    """
    record_data can be a dictionary, tuple, or list of dictionaries or tuples.
    if record_data is a list, it creates multiple records.
    """
    id_value = None
    with engine.begin() as connection:
        result = connection.execute(table.insert(), record_data)
        # If there was only a single record created, return the record.
        if result.rowcount == 1:
            # We need to manually commit insertion so that we can retrieve the record.
            connection.commit()
            id_value = result.inserted_primary_key[0]
            if id_value is not None:
                return get_record(table, engine, id_value)
    # Do not return any records if multiple rows were added.
    return None


def update_record(table, engine, id_value, record_data):
    primary_key_column = _get_primary_key_column(table)
    with engine.begin() as connection:
        connection.execute(
            table.update().where(primary_key_column == id_value).values(record_data)
        )
    return get_record(table, engine, id_value)


def delete_record(table, engine, id_value):
    primary_key_column = _get_primary_key_column(table)
    query = delete(table).where(primary_key_column == id_value)
    with engine.begin() as conn:
        return conn.execute(query)
