from mathesar.models import Table


def test_record_list(create_table, client):
    """
    Desired format:
    {
        "count": 25,
        "results": [
            {
                "mathesar_id": 1,
                "Center": "NASA Kennedy Space Center",
                "Status": "Application",
                "Case Number": "KSC-12871",
                "Patent Number": "0",
                "Application SN": "13/033,085",
                "Title": "Polyimide Wire Insulation Repair System",
                "Patent Expiration Date": ""
            },
            {
                "mathesar_id": 2,
                "Center": "NASA Ames Research Center",
                "Status": "Issued",
                "Case Number": "ARC-14048-1",
                "Patent Number": "5694939",
                "Application SN": "08/543,093",
                "Title": "Autogenic-Feedback Training Exercise Method & System",
                "Patent Expiration Date": "10/03/2015"
            },
            etc.
        ]
    }
    """
    table_name = 'NASA Record List'
    create_table(table_name)
    table = Table.objects.get(name=table_name)

    response = client.get(f'/api/v0/tables/{table.id}/records/')
    response_data = response.json()
    record_data = response_data['results'][0]

    assert response.status_code == 200
    assert response_data['count'] == 1393
    assert len(response_data['results']) == 50
    for column_name in table.sa_column_names:
        assert column_name in record_data


def test_record_list_pagination_limit(create_table, client):
    table_name = 'NASA Record List Pagination Limit'
    create_table(table_name)
    table = Table.objects.get(name=table_name)

    response = client.get(f'/api/v0/tables/{table.id}/records/?limit=5')
    response_data = response.json()
    record_data = response_data['results'][0]

    assert response.status_code == 200
    assert response_data['count'] == 1393
    assert len(response_data['results']) == 5
    for column_name in table.sa_column_names:
        assert column_name in record_data


def test_record_list_pagination_offset(create_table, client):
    table_name = 'NASA Record List Pagination Offset'
    create_table(table_name)
    table = Table.objects.get(name=table_name)

    response_1 = client.get(f'/api/v0/tables/{table.id}/records/?limit=5&offset=5')
    response_1_data = response_1.json()
    record_1_data = response_1_data['results'][0]
    response_2 = client.get(f'/api/v0/tables/{table.id}/records/?limit=5&offset=10')
    response_2_data = response_2.json()
    record_2_data = response_2_data['results'][0]

    assert response_1.status_code == 200
    assert response_2.status_code == 200
    assert response_1_data['count'] == 1393
    assert response_2_data['count'] == 1393
    assert len(response_1_data['results']) == 5
    assert len(response_2_data['results']) == 5

    assert record_1_data['mathesar_id'] != record_2_data['mathesar_id']
    assert record_1_data['Case Number'] != record_2_data['Case Number']
    assert record_1_data['Patent Number'] != record_2_data['Patent Number']
    assert record_1_data['Application SN'] != record_2_data['Application SN']


def test_record_detail(create_table, client):
    table_name = 'NASA Record Detail'
    create_table(table_name)
    table = Table.objects.get(name=table_name)
    record_id = 1
    record = table.get_record(record_id)

    response = client.get(f'/api/v0/tables/{table.id}/records/{record_id}/')
    record_data = response.json()
    record_as_dict = record._asdict()

    assert response.status_code == 200
    for column_name in table.sa_column_names:
        assert column_name in record_data
        assert record_as_dict[column_name] == record_data[column_name]


def test_record_create(create_table, client):
    table_name = 'NASA Record Create'
    create_table(table_name)
    table = Table.objects.get(name=table_name)
    records = table.get_records()
    original_num_records = len(records)

    data = {
        'Center': 'NASA Example Space Center',
        'Status': 'Application',
        'Case Number': 'ESC-0000',
        'Patent Number': '01234',
        'Application SN': '01/000,001',
        'Title': 'Example Patent Name',
        'Patent Expiration Date': ''
    }
    response = client.post(f'/api/v0/tables/{table.id}/records/', data=data)
    record_data = response.json()

    assert response.status_code == 201
    assert len(table.get_records()) == original_num_records + 1
    for column_name in table.sa_column_names:
        assert column_name in record_data
        if column_name in data:
            assert data[column_name] == record_data[column_name]


def test_record_partial_update(create_table, client):
    table_name = 'NASA Record Patch'
    create_table(table_name)
    table = Table.objects.get(name=table_name)
    records = table.get_records()
    record_id = records[0]['mathesar_id']

    original_response = client.get(f'/api/v0/tables/{table.id}/records/{record_id}/')
    original_data = original_response.json()

    data = {
        'Center': 'NASA Example Space Center',
        'Status': 'Example',
    }
    response = client.patch(f'/api/v0/tables/{table.id}/records/{record_id}/', data=data)
    record_data = response.json()

    assert response.status_code == 200
    for column_name in table.sa_column_names:
        assert column_name in record_data
        if column_name in data and column_name not in ['Center', 'Status']:
            assert original_data[column_name] == record_data[column_name]
        elif column_name == 'Center':
            assert original_data[column_name] != record_data[column_name]
            assert record_data[column_name] == 'NASA Example Space Center'
        elif column_name == 'Status':
            assert original_data[column_name] != record_data[column_name]
            assert record_data[column_name] == 'Example'


def test_record_delete(create_table, client):
    table_name = 'NASA Record Delete'
    create_table(table_name)
    table = Table.objects.get(name=table_name)
    records = table.get_records()
    original_num_records = len(records)
    record_id = records[0]['mathesar_id']

    response = client.delete(f'/api/v0/tables/{table.id}/records/{record_id}/')
    assert response.status_code == 204
    assert len(table.get_records()) == original_num_records - 1


def test_record_update(create_table, client):
    table_name = 'NASA Record Put'
    create_table(table_name)
    table = Table.objects.get(name=table_name)
    records = table.get_records()
    record_id = records[0]['mathesar_id']

    data = {
        'Center': 'NASA Example Space Center',
        'Status': 'Example',
    }
    response = client.put(f'/api/v0/tables/{table.id}/records/{record_id}/', data=data)
    assert response.status_code == 405
    assert response.json()['detail'] == 'Method "PUT" not allowed.'


def test_record_404(create_table, client):
    table_name = 'NASA Record 404'
    create_table(table_name)
    table = Table.objects.get(name=table_name)
    records = table.get_records()
    record_id = records[0]['mathesar_id']

    client.delete(f'/api/v0/tables/{table.id}/records/{record_id}/')
    response = client.get(f'/api/v0/tables/{table.id}/records/{record_id}/')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Not found.'
