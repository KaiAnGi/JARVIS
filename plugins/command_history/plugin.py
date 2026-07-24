"""command_history plugin - Voice access to command history."""

from core.database import get_command_history
from core.language import resp, get_lang


def init(bus):
    pass


def handle(action: str, text: str, bus):
    if action == "last_command":
        commands = get_command_history(limit=1)
        if commands:
            c = commands[0]
            bus.emit("speak", resp("last_command",
                                   action=c["action"],
                                   text=c["parameters"]))
        else:
            bus.emit("speak", resp("history_empty"))

    elif action == "command_history":
        commands = get_command_history(limit=5)
        if not commands:
            bus.emit("speak", resp("history_empty"))
            return
        lines = []
        for i, c in enumerate(commands, 1):
            lines.append(f"{i}. {c['parameters']}")
        bus.emit("speak", resp("history_list", commands="\n".join(lines)))

    elif action == "clear_history":
        from core.database import _connect
        with _connect() as conn:
            conn.execute("DELETE FROM commands")
        bus.emit("speak", resp("history_cleared"))
