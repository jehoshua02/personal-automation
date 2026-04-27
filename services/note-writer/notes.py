import os
import re


class NoteWriter:
    def __init__(self, notes_dir: str = "/data/notes"):
        self.notes_dir = notes_dir
        os.makedirs(self.notes_dir, exist_ok=True)

    def build_filename(self, date: str, topic: str) -> str:
        slug = re.sub(r"[^a-z0-9-]", "-", topic.lower().strip())
        slug = re.sub(r"-+", "-", slug).strip("-")
        return f"{date}-{slug}.md"

    def write_note(self, title: str, content: str, topic: str, date: str, email_link: str) -> str:
        filename = self.build_filename(date, topic)
        path = os.path.join(self.notes_dir, filename)
        if os.path.exists(path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(path):
                path = os.path.join(self.notes_dir, f"{base}-{counter}{ext}")
                counter += 1
        body = f"# {title}\n\n**Date:** {date}\n"
        if email_link:
            body += f"**Source:** {email_link}\n"
        body += f"\n{content}\n"
        with open(path, "w") as f:
            f.write(body)
        return path
