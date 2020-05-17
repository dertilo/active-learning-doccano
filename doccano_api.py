import json
import os
from http import HTTPStatus
from pprint import pprint
from typing import Dict, List
import requests
from util.data_io import read_jsonl

path = os.path.dirname(os.path.abspath(__file__))
with open(path + "/config.json") as f:
    config = json.loads(f.read())
ADMIN_USER_NAME = config["user_name"]
ADMIN_PASSWORD = config["password"]
HOST = config["host"]
PORT = config["port"]


def obtain_auth_token(user_name=ADMIN_USER_NAME, password=ADMIN_PASSWORD):
    url = "http://%s:%d/v1/auth-token" % (HOST, PORT)
    response = requests.post(url, data={"username": user_name, "password": password})
    if response.status_code != HTTPStatus.OK:
        print(response.status_code)
        print(response.json())
    return response.json()["token"]


ADMIN_TOKEN = obtain_auth_token(ADMIN_USER_NAME, ADMIN_PASSWORD)


def create_documents(docs: List[Dict], project_id: int, user_id: int):
    url = "http://%s:%d/v1/projects/%d/docs/upload" % (HOST, PORT, project_id)

    s = "\n".join([json.dumps(d) for d in docs])
    response = requests.post(
        url,
        data={"format": "json", "user_id": int(user_id)},
        files={"file": s},
        headers={"Authorization": "token %s" % ADMIN_TOKEN},
    )

    if response.status_code != HTTPStatus.CREATED:
        print(response.status_code)
        print(response.json())

    assert response.status_code == HTTPStatus.CREATED


def list_documents(
    project_id: int, user_name=ADMIN_USER_NAME, password=ADMIN_PASSWORD
) -> List[Dict]:
    url = "http://%s:%d/v1/projects/%d/docs" % (HOST, PORT, project_id)

    token = obtain_auth_token(user_name, password)
    response = requests.get(url, headers={"Authorization": "token %s" % token})

    if response.status_code != HTTPStatus.OK:
        print(response.status_code)
        print(response.json())

    return response.json()["results"]


def get_document(project_id, doc_id):
    url = "http://%s:%d/v1/projects/%d/docs/%d" % (HOST, PORT, project_id, doc_id)

    response = requests.get(url, headers={"Authorization": "token %s" % ADMIN_TOKEN})
    assert response.status_code == HTTPStatus.OK
    return response.json()


def delete_document(project_id, doc_id):
    url = "http://%s:%d/v1/projects/%d/docs/%d" % (HOST, PORT, project_id, doc_id)

    response = requests.delete(url, headers={"Authorization": "token %s" % ADMIN_TOKEN})
    if response.status_code != HTTPStatus.NO_CONTENT:
        print(response.status_code)
        print(response.json())


def delete_project(project_id):
    url = "http://%s:%d/v1/projects/%d" % (HOST, PORT, project_id)

    response = requests.delete(url, headers={"Authorization": "token %s" % ADMIN_TOKEN})
    if response.status_code != HTTPStatus.NO_CONTENT:
        print(response.status_code)
        print(response.json())


def delete_user(user_id: int):
    assert isinstance(user_id, int)
    url = "http://%s:%d/v1/users/%d" % (HOST, PORT, user_id)

    response = requests.delete(url, headers={"Authorization": "token %s" % ADMIN_TOKEN})
    if response.status_code != HTTPStatus.NO_CONTENT:
        print(response.status_code)
        print(response.json())


def get_me():
    url = "http://%s:%d/v1/me" % (HOST, PORT)
    response = requests.get(url, headers={"Authorization": "token %s" % ADMIN_TOKEN})
    return response.json()


def create_user(
    username, password, user_id=None, first_name="", last_name="", email=""
):

    url = "http://%s:%d/v1/users" % (HOST, PORT)

    user_data = {
        "username": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
    }
    if user_id:
        user_data["id"] = user_id

    response = requests.post(
        url, data=user_data, headers={"Authorization": "token %s" % ADMIN_TOKEN}
    )

    if response.status_code != HTTPStatus.CREATED:
        print(response.status_code)
        print(response.json())

    assert response.status_code == HTTPStatus.CREATED
    return response.json()


def create_project(project_name="testproject", users: List[int] = None):

    url = "http://%s:%d/v1/projects" % (HOST, PORT)

    data = {
        "name": project_name,
        "project_type": "SequenceLabeling",
        "collaborative_annotation": True,
        "description": "example",
        "guideline": "example",
        "resourcetype": "SequenceLabelingProject",
    }

    response = requests.post(
        url, data=data, headers={"Authorization": "token %s" % ADMIN_TOKEN}
    )

    if response.status_code != HTTPStatus.CREATED:
        print(response.status_code)
        print(response.json())

    created_project = response.json()
    edit_project(created_project["id"], users=users)
    assert response.status_code == HTTPStatus.CREATED


def list_users() -> List[Dict]:
    url = "http://%s:%d/v1/users" % (HOST, PORT)

    response = requests.get(url, headers={"Authorization": "token %s" % ADMIN_TOKEN})

    if response.status_code != HTTPStatus.OK:
        print(response.status_code)
        print(response.json())

    return response.json()


def list_projects() -> List[Dict]:
    url = "http://%s:%d/v1/projects" % (HOST, PORT)

    response = requests.get(url, headers={"Authorization": "token %s" % ADMIN_TOKEN})
    if response.status_code != HTTPStatus.OK:
        print(response.status_code)
        print(response.json())

    return response.json()


def purge_project_documents(project_id):
    [
        delete_document(project_id=project_id, doc_id=d["id"])
        for d in list_documents(project_id)
    ]


def purge_users():
    [delete_user(d["id"]) for d in list_users() if d["username"] != "admin"]


def edit_project(project_id, **kwargs):
    url = "http://%s:%d/v1/projects/%d" % (HOST, PORT, project_id)
    keys = ["name", "description", "guideline", "project_type", "users"]
    params = {k: v for k, v in kwargs.items() if k in keys}
    response = requests.patch(
        url, data=params, headers={"Authorization": "token %s" % ADMIN_TOKEN}
    )

    if response.status_code != HTTPStatus.OK:
        print(response.status_code)
        print(response.text)

    assert response.status_code == HTTPStatus.OK


def add_all_user_to_project(project_id: int):
    user_ids = [d["id"] for d in list_users()]
    edit_project(project_id, users=user_ids)


def dummy_project_user_documents():
    user_id = 33
    if len(list_projects()) == 0:
        create_project(project_name="testproject")
    if len(list_users()) == 1:
        create_user("user", "password", user_id)

    project_id = next(iter(list_projects()))["id"]
    add_all_user_to_project(project_id)
    DATA_DIR = "."
    filename = "sample_docs.jsonl"
    jsonl_file = os.path.join(DATA_DIR, filename)
    docs = read_jsonl(jsonl_file)
    # user_id = [u['id'] for u in list_users() if u['id']!=1][0]
    create_documents(docs, project_id=project_id, user_id=user_id)


def purge_projects():
    [delete_project(p["id"]) for p in list_projects()]


def purge():
    purge_users()
    purge_projects()


if __name__ == "__main__":
    # purge()
    pprint(list_users())
    # create_user('user', 'password', 33)
    # dummy_project_user_documents()
