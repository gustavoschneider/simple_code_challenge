import json

from fastapi.testclient import TestClient
from main import app


client = TestClient(app)

def test_get_account_success():
    expected_response = {
        'account_id': 1,
        'account_balance': 1000,
        'account_saving': 1
    }

    response = client.get('/1')
    assert response.status_code == 200
    assert response.json() == expected_response

def test_get_account_not_found():
    expected_response = {
        'detail': 'Account not found!'
    }

    response = client.get('/2')
    assert response.status_code == 404
    assert response.json() == expected_response

def test_saving_movement_sucess():
    expected_response = {
        'amount': 100,
        'description': 'Moving from balance to savings'
    }
    response = client.post('/1/savings', data=json.dumps({'amount': 100}))

    assert response.status_code == 200
    assert response.json()['amount'] == expected_response['amount']
    assert response.json()['description'] == expected_response['description']

def test_saving_movement_have_not_fund():
    expected_response = {'detail': 'Account does not have funds.'}

    response = client.post('/1/savings', data=json.dumps({'amount': 10000}))

    assert response.status_code == 400
    assert response.json() == expected_response

def test_withdraw_movement_sucess():
    expected_response = {
        'amount': 100,
        'description': 'Moving from savings to balance'
    }
    response = client.post('/1/withdraw', data=json.dumps({'amount': 100}))

    assert response.status_code == 200
    assert response.json()['amount'] == expected_response['amount']
    assert response.json()['description'] == expected_response['description']

def test_withdraw_movement_have_not_fund():
    expected_response = {'detail': 'Account savings does not have funds.'}

    response = client.post('/1/withdraw', data=json.dumps({'amount': 10000}))

    assert response.status_code == 400
    assert response.json() == expected_response


def test_movements_success():
    expected_response = {
        'account': {
            'account_id': 1,
            'account_balance': 900,
            'account_saving': 101
        },
        'movements': [
            {
            'movement_id': 1,
            'amount': 100,
            'description': 'Moving from balance to savings',
            }
        ]
    }
    response = client.post('/1/savings', data=json.dumps({'amount': 100}))
    assert response.status_code == 200

    response = client.get('/1/movements')
    assert response.json()['account']['account_id'] == expected_response['account']['account_id']
    assert response.json()['account']['account_balance'] == expected_response['account']['account_balance']
    assert response.json()['account']['account_saving'] == expected_response['account']['account_saving']
    
    assert response.json()['movements'][0]['amount'] == expected_response['movements'][0]['amount']
    assert response.json()['movements'][0]['description'] == expected_response['movements'][0]['description']
