import os

from core.app import App
from core.event import BACK, NAV_NEXT, NAV_PREVIOUS, SELECT
from ui.dialog import Dialog
from ui.theme import Theme

LIST_Y = Theme.CONTENT_Y
ROW_HEIGHT = 12
VISIBLE_ROWS = 3
NAME_CHARS = 10
TAG_CHARS = 5
DIR_MODE = 0x4000


class FileManager(App):
    """Simple file browser.

    O/N move, T+H enters a directory or asks before deleting a file,
    P+Y goes up one directory (leaves the app at the root). The list
    shows each file's size; the footer shows the exact byte count of
    the selected entry.
    """

    name = "Files"

    MODE_LIST = 0
    MODE_CONFIRM = 1
    MODE_ERROR = 2

    def open(self):
        self.cwd = "/"
        self.entries = []
        self.index = 0
        self.offset = 0
        self.mode = self.MODE_LIST
        self.dialog = None
        self._load()

    # --- directory model ---

    def _path(self, name=None):
        if name is None:
            return self.cwd
        if self.cwd == "/":
            return "/" + name
        return self.cwd + "/" + name

    def _load(self):
        try:
            names = os.listdir(self.cwd)
        except OSError:
            names = []
        entries = []
        for entry in names:
            try:
                st = os.stat(self._path(entry))
            except OSError:
                continue
            is_dir = bool(st[0] & DIR_MODE)
            entries.append((entry, is_dir, 0 if is_dir else st[6]))
        entries.sort(key=lambda item: (0 if item[1] else 1, item[0]))
        self.entries = entries
        if self.index >= len(entries):
            self.index = max(0, len(entries) - 1)
        self._sync_window()

    def _sync_window(self):
        if self.index < self.offset:
            self.offset = self.index
        if self.index >= self.offset + VISIBLE_ROWS:
            self.offset = self.index - VISIBLE_ROWS + 1
        if self.offset < 0:
            self.offset = 0

    def _go_up(self):
        if self.cwd == "/":
            return False
        parent = self.cwd.rsplit("/", 1)[0]
        self.cwd = parent if parent else "/"
        self.index = 0
        self.offset = 0
        self._load()
        return True

    def _delete_selected(self):
        name, is_dir, _ = self.entries[self.index]
        if is_dir:
            return
        try:
            os.remove(self._path(name))
            self._close_dialog()
            self._load()
        except OSError:
            self.mode = self.MODE_ERROR
            self.dialog = Dialog("Error", "Delete failed", ["OK"])

    def _close_dialog(self):
        self.mode = self.MODE_LIST
        self.dialog = None

    # --- formatting ---

    @staticmethod
    def _fmt_size(size):
        if size >= 1048576:
            return "%dM" % (size // 1048576)
        if size >= 1024:
            return "%dK" % (size // 1024)
        return "%dB" % size

    def _header(self):
        path = self.cwd
        if len(path) > 16:
            path = "~" + path[-15:]
        return path

    def _row_text(self, i):
        name, is_dir, size = self.entries[i]
        tag = "<dir>" if is_dir else self._fmt_size(size)
        shown = name[:NAME_CHARS]
        text = shown + " " * (NAME_CHARS - len(shown))
        if len(tag) < TAG_CHARS:
            text += " " * (TAG_CHARS - len(tag)) + tag
        else:
            text += tag[:TAG_CHARS]
        return (">" if i == self.index else " ") + text

    def _footer(self):
        if not self.entries:
            return "Empty"
        name, is_dir, size = self.entries[self.index]
        if is_dir:
            return "Directory"
        if size >= 1048576:
            return "Size: %dK" % (size // 1024)
        return "Size: %dB" % size

    # --- events ---

    def on_event(self, event):
        if self.mode == self.MODE_CONFIRM:
            return self._on_event_confirm(event)
        if self.mode == self.MODE_ERROR:
            if event.type in (SELECT, BACK):
                self._close_dialog()
                return True
            return None
        return self._on_event_list(event)

    def _on_event_confirm(self, event):
        dialog = self.dialog
        if dialog is None:
            self._close_dialog()
            return True
        if event.type == BACK:
            self._close_dialog()
            return True
        if event.type == NAV_NEXT:
            dialog.next()
            return True
        if event.type == NAV_PREVIOUS:
            dialog.previous()
            return True
        if event.type == SELECT:
            if dialog.selected() == "Yes":
                self._delete_selected()
            else:
                self._close_dialog()
            return True
        return None

    def _on_event_list(self, event):
        if event.type == BACK:
            if self._go_up():
                return True
            return BACK
        if not self.entries:
            return None
        if event.type == NAV_NEXT:
            self.index = (self.index + 1) % len(self.entries)
            self._sync_window()
            return True
        if event.type == NAV_PREVIOUS:
            self.index = (self.index - 1) % len(self.entries)
            self._sync_window()
            return True
        if event.type == SELECT:
            name, is_dir, _ = self.entries[self.index]
            if is_dir:
                self.cwd = self._path(name)
                self.index = 0
                self.offset = 0
                self._load()
                return True
            shown = name if len(name) <= 16 else name[:16]
            self.mode = self.MODE_CONFIRM
            self.dialog = Dialog("Delete?", shown, ["No", "Yes"])
            return True
        return None

    def update(self, delta_ms=0):
        return False

    # --- drawing ---

    def draw(self, display):
        if self.dialog is not None:
            self.dialog.draw(display)
            return
        display.text(self._header(), 0, Theme.TITLE_Y)
        bottom = self.offset + VISIBLE_ROWS
        if bottom > len(self.entries):
            bottom = len(self.entries)
        for i in range(self.offset, bottom):
            display.text(self._row_text(i), 0,
                         LIST_Y + (i - self.offset) * ROW_HEIGHT)
        display.text(self._footer(), 0, Theme.FOOTER_Y)


def _icon(canvas):
    canvas.rect(3, 5, 9, 5)
    canvas.rect(3, 9, 18, 10)


MANIFEST = {
    "name": "Files",
    "version": "0.1",
    "description": "Browse directories, view sizes, delete files",
    "icon": _icon,
}

APP_CLASS = FileManager
