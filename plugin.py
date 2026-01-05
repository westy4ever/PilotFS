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

# Setup logging early
try:
    from Plugins.Extensions.PilotFS.utils.logging_config import setup_logging, get_logger
    logger = get_logger(__name__)
except Exception as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.error("Failed to setup logging: %s" % str(e))

def main(session, **kwargs):
    """Main entry point for the plugin"""
    import traceback
    import sys
    
    try:
        logger.info("Starting PilotFS Platinum v6.1")
        logger.info("Python path: %s" % str(sys.path[:3]))
        
        # Try to import main screen
        logger.info("Attempting to import PilotFSMain...")
        try:
            from Plugins.Extensions.PilotFS.ui.main_screen import PilotFSMain
            logger.info("Successfully imported PilotFSMain: %s" % str(PilotFSMain))
        except ImportError as ie:
            logger.error("Import error: %s" % str(ie))
            logger.error("Full traceback:\n%s" % traceback.format_exc())
            raise
        
        # Open the main screen
        logger.info("Opening PilotFSMain screen...")
        session.open(PilotFSMain)
        logger.info("PilotFS started successfully")
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        logger.error("Failed to start PilotFS: %s" % error_msg)
        logger.error("Traceback:\n%s" % error_trace)
        
        # Show error to user
        try:
            from Screens.MessageBox import MessageBox
            session.open(
                MessageBox,
                "Failed to start PilotFS:\n\n%s\n\nCheck /tmp/pilotfs.log" % error_msg,
                MessageBox.TYPE_ERROR,
                timeout=10
            )
        except Exception as msg_error:
            logger.error("Could not show error message: %s" % str(msg_error))

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
