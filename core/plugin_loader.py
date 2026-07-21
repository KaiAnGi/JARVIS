"""Plugin discovery and registration."""

import importlib.util
from pathlib import Path

from core.language import all_patterns


PLUGINS_DIR = Path(__file__).parent.parent / "plugins"


def load_plugins(bus, router):
    """Discover and load all plugins from plugins/ directory."""
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir():
            continue

        plugin_path = plugin_dir / "plugin.py"
        if not plugin_path.exists():
            continue

        name = plugin_dir.name

        try:
            spec = importlib.util.spec_from_file_location(name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "init"):
                module.init(bus)

            router._plugins[name] = module
            print(f"[PLUGIN] Loaded: {name}")
        except Exception as e:
            print(f"[PLUGIN] Failed to load {plugin_dir.name}: {e}")

    router.rebuild_patterns()
