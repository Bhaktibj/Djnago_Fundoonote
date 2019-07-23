import requests

main_url = 'http://localhost:8000'

def test_create_note_invalid():
    url = main_url + "/Notes/Create/"
    data = {'title': 'Bhakti', 'description': 'Hii How You', 'color': "Red"}
    resp = requests.post(url, data=data)
    print("Hello", resp.status_code)
    assert resp.status_code == 401


def test_create_valid():
    url = main_url + "/Notes/Detail/1/"
    data = {'text': 'Welcom 123','pub_date':'2019-07-16T11:15:05.826592Z', 'created_By': 1}
    response = requests.get(url,data=data)
    print("hello", response.status_code)
    assert response.status_code == 401

