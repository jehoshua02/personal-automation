import requests

TASKS_API = "https://tasks.googleapis.com/tasks/v1"


class TaskWriter:
    def __init__(self, auth_service_url: str, task_list_name: str = "Auto-Extracted"):
        self.auth_service_url = auth_service_url
        self.task_list_name = task_list_name
        self._list_id_cache = None

    def get_token(self) -> str:
        resp = requests.get(f"{self.auth_service_url}/token")
        if resp.status_code != 200:
            raise Exception(f"Auth service returned {resp.status_code}")
        return resp.json()["access_token"]

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.get_token()}"}

    def get_or_create_task_list(self) -> str:
        if self._list_id_cache:
            return self._list_id_cache
        resp = requests.get(f"{TASKS_API}/users/@me/lists", headers=self._headers())
        lists = resp.json().get("items", [])
        for tl in lists:
            if tl["title"] == self.task_list_name:
                self._list_id_cache = tl["id"]
                return tl["id"]
        resp = requests.post(
            f"{TASKS_API}/users/@me/lists",
            headers=self._headers(),
            json={"title": self.task_list_name},
        )
        result = resp.json()
        self._list_id_cache = result["id"]
        return result["id"]

    def write_task(self, title: str, description: str, due_date: str, email_link: str) -> dict:
        list_id = self.get_or_create_task_list()
        body = {
            "title": title,
            "notes": f"{description}\n\nSource: {email_link}",
        }
        if due_date:
            body["due"] = f"{due_date}T00:00:00.000Z"
        resp = requests.post(
            f"{TASKS_API}/lists/{list_id}/tasks",
            headers=self._headers(),
            json=body,
        )
        return resp.json()
