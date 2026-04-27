from email.utils import parsedate_to_datetime
import requests


class Pipeline:
    def __init__(self, gmail_reader_url: str, llm_processor_url: str,
                 task_writer_url: str, calendar_writer_url: str, note_writer_url: str,
                 email_filter_url: str = "",
                 filtered_label: str = "AutoFiltered"):
        self.gmail_reader_url = gmail_reader_url
        self.llm_processor_url = llm_processor_url
        self.task_writer_url = task_writer_url
        self.calendar_writer_url = calendar_writer_url
        self.note_writer_url = note_writer_url
        self.email_filter_url = email_filter_url
        self.filtered_label = filtered_label

    def fetch_messages(self, max_results: int = 10) -> list[dict]:
        resp = requests.post(
            f"{self.gmail_reader_url}/fetch",
            json={"max_results": max_results},
        )
        return resp.json().get("messages", [])

    def process_message(self, message: dict) -> dict:
        resp = requests.post(
            f"{self.llm_processor_url}/extract",
            json={
                "subject": message.get("subject", ""),
                "body": message.get("body", ""),
                "from": message.get("from", ""),
                "date": message.get("date", ""),
            },
        )
        return resp.json()

    def route_extractions(self, extractions: dict, email_link: str, date: str = "") -> dict:
        results = {"tasks": [], "events": [], "notes": []}
        for task in extractions.get("tasks", []):
            resp = requests.post(
                f"{self.task_writer_url}/write",
                json={**task, "email_link": email_link},
            )
            results["tasks"].append(resp.json())
        for event in extractions.get("events", []):
            resp = requests.post(
                f"{self.calendar_writer_url}/write",
                json={**event, "email_link": email_link},
            )
            results["events"].append(resp.json())
        for note in extractions.get("notes", []):
            resp = requests.post(
                f"{self.note_writer_url}/write",
                json={**note, "email_link": email_link, "date": date},
            )
            results["notes"].append(resp.json())
        return results

    def filter_message(self, message: dict) -> dict:
        try:
            resp = requests.post(
                f"{self.email_filter_url}/filter",
                json={
                    "subject": message.get("subject", ""),
                    "body": message.get("body", ""),
                    "from": message.get("from", ""),
                    "date": message.get("date", ""),
                },
            )
            return resp.json()
        except Exception:
            return {"important": True, "reason": "Filter unavailable", "method": "error"}

    def mark_processed(self, message_id: str, label: str = "processed"):
        requests.post(
            f"{self.gmail_reader_url}/mark-processed",
            json={"message_id": message_id, "label": label},
        )

    def run(self, max_results: int = 10) -> list[dict]:
        messages = self.fetch_messages(max_results=max_results)
        results = []
        for msg in messages:
            filter_result = self.filter_message(msg)
            if not filter_result.get("important", True):
                self.mark_processed(msg["id"], label=self.filtered_label)
                results.append({
                    "message_id": msg["id"],
                    "subject": msg.get("subject", ""),
                    "filtered": True,
                    "filter_reason": filter_result.get("reason", ""),
                })
                continue
            extractions = self.process_message(msg)
            raw_date = msg.get("date", "")
            try:
                clean_date = parsedate_to_datetime(raw_date).strftime("%Y-%m-%d")
            except Exception:
                clean_date = raw_date
            write_results = self.route_extractions(extractions, msg.get("link", ""), clean_date)
            self.mark_processed(msg["id"])
            results.append({
                "message_id": msg["id"],
                "subject": msg.get("subject", ""),
                "extractions": extractions,
                "write_results": write_results,
            })
        return results
