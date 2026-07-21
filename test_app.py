import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# 单元测试函数 1：测试根接口响应是否正常
def test_hello_endpoint(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"success" in response.data