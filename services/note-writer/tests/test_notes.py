import os
import pytest
from notes import NoteWriter


@pytest.fixture
def writer(tmp_path):
    return NoteWriter(notes_dir=str(tmp_path))


class TestBuildFilename:
    def test_includes_date(self, writer):
        filename = writer.build_filename("2026-04-27", "api-keys")
        assert "2026-04-27" in filename

    def test_includes_topic_slug(self, writer):
        filename = writer.build_filename("2026-04-27", "api-keys")
        assert "api-keys" in filename

    def test_ends_with_md(self, writer):
        filename = writer.build_filename("2026-04-27", "test")
        assert filename.endswith(".md")

    def test_handles_spaces_in_topic(self, writer):
        filename = writer.build_filename("2026-04-27", "my cool topic")
        assert " " not in filename


class TestWriteNote:
    def test_creates_file(self, writer):
        writer.write_note(
            title="API Keys",
            content="Key: abc123",
            topic="api-keys",
            date="2026-04-27",
            email_link="https://mail.google.com/mail/u/0/#inbox/msg1",
        )
        files = os.listdir(writer.notes_dir)
        assert len(files) == 1
        assert files[0].endswith(".md")

    def test_includes_title(self, writer):
        path = writer.write_note(
            title="API Keys", content="Key: abc123", topic="api-keys",
            date="2026-04-27", email_link="",
        )
        with open(path) as f:
            content = f.read()
        assert "# API Keys" in content

    def test_includes_email_link(self, writer):
        path = writer.write_note(
            title="T", content="C", topic="t", date="2026-04-27",
            email_link="https://mail.google.com/mail/u/0/#inbox/msg1",
        )
        with open(path) as f:
            content = f.read()
        assert "msg1" in content

    def test_includes_date(self, writer):
        path = writer.write_note(
            title="T", content="C", topic="t", date="2026-04-27", email_link="",
        )
        with open(path) as f:
            content = f.read()
        assert "2026-04-27" in content

    def test_no_overwrite_existing(self, writer):
        writer.write_note(title="T", content="First", topic="t", date="2026-04-27", email_link="")
        writer.write_note(title="T", content="Second", topic="t", date="2026-04-27", email_link="")
        files = os.listdir(writer.notes_dir)
        assert len(files) == 2
