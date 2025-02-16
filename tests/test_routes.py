import pytest
import json

def test_auth_new_user(client):
    response = client.post('/api/auth', json={
        'username': 'newuser',
        'password': 'password'
    })
    assert response.status_code == 200
    assert 'token' in response.json

def test_auth_existing_user(client, test_user):
    response = client.post('/api/auth', json={
        'username': 'testuser',
        'password': 'password'
    })
    assert response.status_code == 200
    assert 'token' in response.json

def test_get_info(client, test_user):
    auth_response = client.post('/api/auth', json={
        'username': 'testuser',
        'password': 'password'
    })
    token = auth_response.json['token']
    
    response = client.get('/api/info', 
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['coins'] == 1000
    assert 'inventory' in response.json
    assert 'coinHistory' in response.json

def test_send_coin(client, test_user):
    client.post('/api/auth', json={
        'username': 'receiver',
        'password': 'password'
    })
    
    auth_response = client.post('/api/auth', json={
        'username': 'testuser',
        'password': 'password'
    })
    token = auth_response.json['token']
    
    response = client.post('/api/sendCoin',
                          headers={'Authorization': f'Bearer {token}'},
                          json={'toUser': 'receiver', 'amount': 100})
    assert response.status_code == 200

def test_buy_item(client, test_user):
    auth_response = client.post('/api/auth', json={
        'username': 'testuser',
        'password': 'password'
    })
    token = auth_response.json['token']
    
    response = client.get('/api/buy/cup',
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200