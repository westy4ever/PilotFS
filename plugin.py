#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
PilotFS Platinum v6.1 - Professional File Manager for Enigma2
Enhanced with Smart Context Menus & Remote Access
"""

# Translation support
try:
    import language
    from Tools.Directories import resolveFilename, SCOPE_PLUGINS
    import gettext
    import os
    
    lang = language.getLanguage()[:2]
    os.environ["LANGUAGE"] = lang
    gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_PLUGINS))
    gettext.textdomain("enigma2")
    _ = gettext.gettext
except ImportError:
    # Fallback: no translation
    def _(txt):
        return txt

from Plugins.Plugin import PluginDescriptor
from .ui.main_screen import PilotFSMain
from .utils.logging_config import setup_logging, get_logger

# Setup logging
logger = get_logger(__name__)

def main(session, **kwargs):
    """Main entry point for the plugin"""
    try:
        logger.info("Starting PilotFS Platinum v6.1")
        session.open(PilotFSMain)
    except Exception as e:
        logger.error(f"Failed to start PilotFS: {e}")
        from Screens.MessageBox import MessageBox
        session.open(MessageBox, f"Failed to start PilotFS:\n{e}", MessageBox.TYPE_ERROR)

def menu(menuid, **kwargs):
    """Plugin menu integration"""
    if menuid == "mainmenu":
        return [(_("PilotFS Platinum"), main, "pilotfs", 46)]
    return []

def Plugins(**kwargs):
    """Plugin descriptor"""
    description = _("Professional File Manager with Smart Context Menus")
    
    return [
        PluginDescriptor(
            name="PilotFS Platinum v6.1",
            description=description,
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon="pilotfs.png",
            fnc=main
        ),
        PluginDescriptor(
            name="PilotFS Platinum",
            description=description,
            where=PluginDescriptor.WHERE_MENU,
            fnc=menu
        )
    ]

if __name__ == "__main__":
    # Test mode
    print("PilotFS Platinum v6.1 - Professional File Manager")
    print("This plugin runs within Enigma2 environment.")