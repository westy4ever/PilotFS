"""
Constants for PilotFS Plugin
"""

# ============================================================================
# FILE OPERATION CONSTANTS
# ============================================================================

# Default CIFS/SMB version for mounting
DEFAULT_CIFS_VERSION = "3.0"

# Default timeout for operations (seconds)
DEFAULT_TIMEOUT = 30

# Default ports for network protocols
DEFAULT_FTP_PORT = 21
DEFAULT_SFTP_PORT = 22

# ============================================================================
# PATH CONSTANTS
# ============================================================================

# Configuration and data files
BOOKMARKS_FILE = "/etc/enigma2/pilotfs_bookmarks.json"
REMOTE_CONNECTIONS_FILE = "/etc/enigma2/pilotfs_connections.json"
TRASH_PATH = "/tmp/pilotfs_trash"
CACHE_DIR = "/tmp/pilotfs_cache"
CACHE_FILE = "/tmp/pilotfs_cache.db"  # Added missing CACHE_FILE

# Logging
LOG_FILE = "/tmp/pilotfs.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5

# ============================================================================
# UI CONSTANTS
# ============================================================================

# File list display
MAX_FILENAME_DISPLAY = 40
MAX_PATH_DISPLAY = 60

# Preview settings
MAX_PREVIEW_SIZE = 1024 * 1024  # 1 MB
IMAGE_PREVIEW_SIZE = (400, 300)
TEXT_PREVIEW_LINES = 50

# ============================================================================
# ICON CONSTANTS
# ============================================================================

# Paths to icon directories
ICONS_FOLDER = "/usr/lib/enigma2/python/Plugins/Extensions/PilotFS/icons/"
ICONS_FOLDER_SMALL = ICONS_FOLDER + "small/"
ICONS_FOLDER_LARGE = ICONS_FOLDER + "large/"

# Icon filenames - Individual constants
ICON_FOLDER = "folder.png"
ICON_FILE = "file.png"
ICON_IMAGE = "image.png"
ICON_VIDEO = "video.png"
ICON_AUDIO = "audio.png"
ICON_ARCHIVE = "archive.png"
ICON_DOCUMENT = "document.png"
ICON_SCRIPT = "script.png"
ICON_CONFIG = "config.png"
ICON_TEXT = "text.png"
ICON_BINARY = "binary.png"
ICON_PDF = "pdf.png"
ICON_ZIP = "zip.png"
ICON_EXECUTABLE = "executable.png"
ICON_BACK = "back.png"
ICON_UP = "up.png"
ICON_HOME = "home.png"
ICON_REFRESH = "refresh.png"
ICON_NETWORK = "network.png"
ICON_SETTINGS = "settings.png"
ICON_COPY = "copy.png"
ICON_MOVE = "move.png"
ICON_DELETE = "delete.png"
ICON_RENAME = "rename.png"
ICON_SEARCH = "search.png"
ICON_INFO = "info.png"
ICON_PLAY = "play.png"
ICON_EDIT = "edit.png"
ICON_DOWNLOAD = "download.png"
ICON_UPLOAD = "upload.png"
ICON_CONNECT = "connect.png"
ICON_DISCONNECT = "disconnect.png"
ICON_OK = "ok.png"
ICON_CANCEL = "cancel.png"
ICON_HELP = "help.png"
ICON_EXIT = "exit.png"
ICON_FTP = "ftp.png"
ICON_SFTP = "sftp.png"
ICON_SMB = "smb.png"
ICON_NFS = "nfs.png"

# Icon dictionary for backward compatibility
ICONS = {
    'folder': ICON_FOLDER,
    'file': ICON_FILE,
    'image': ICON_IMAGE,
    'video': ICON_VIDEO,
    'audio': ICON_AUDIO,
    'archive': ICON_ARCHIVE,
    'document': ICON_DOCUMENT,
    'script': ICON_SCRIPT,
    'config': ICON_CONFIG,
    'text': ICON_TEXT,
    'binary': ICON_BINARY,
    'pdf': ICON_PDF,
    'zip': ICON_ZIP,
    'executable': ICON_EXECUTABLE,
    'back': ICON_BACK,
    'up': ICON_UP,
    'home': ICON_HOME,
    'refresh': ICON_REFRESH,
    'network': ICON_NETWORK,
    'settings': ICON_SETTINGS,
    'copy': ICON_COPY,
    'move': ICON_MOVE,
    'delete': ICON_DELETE,
    'rename': ICON_RENAME,
    'search': ICON_SEARCH,
    'info': ICON_INFO,
    'play': ICON_PLAY,
    'edit': ICON_EDIT,
    'download': ICON_DOWNLOAD,
    'upload': ICON_UPLOAD,
    'connect': ICON_CONNECT,
    'disconnect': ICON_DISCONNECT,
    'ok': ICON_OK,
    'cancel': ICON_CANCEL,
    'help': ICON_HELP,
    'exit': ICON_EXIT,
    'ftp': ICON_FTP,
    'sftp': ICON_SFTP,
    'smb': ICON_SMB,
    'nfs': ICON_NFS,
}

# ============================================================================
# NETWORK CONSTANTS (AJPanel-style enhancements)
# ============================================================================

# Network timeouts
DEFAULT_PING_TIMEOUT = 2
DEFAULT_PORT_SCAN_TIMEOUT = 1
DEFAULT_NETWORK_TIMEOUT = 3
MAX_RECONNECT_ATTEMPTS = 3
NETWORK_LOG_SIZE = 1000

# Common service ports (for port scanning)
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 993, 995, 3306, 3389, 8080, 9090]
SMB_PORTS = [139, 445]
FTP_PORTS = [21]
SSH_PORTS = [22]
WEB_PORTS = [80, 443, 8080, 8443]

# Network scan ranges (for network discovery)
NETWORK_SCAN_RANGES = [
    "192.168.0",
    "192.168.1", 
    "192.168.2",
    "192.168.10",
    "192.168.100",
]

# Service identification
SERVICE_PORTS = {
    21: "FTP",
    22: "SSH/SFTP",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB/CIFS",
    993: "IMAPS",
    995: "POP3S",
    1433: "MSSQL",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8080: "HTTP Proxy",
    9090: "Enigma2 WebIf"
}

# Network diagnostic files
NETWORK_INFO_FILES = [
    "/etc/resolv.conf",
    "/etc/hosts",
    "/proc/net/route",
    "/proc/net/dev"
]

# Connection status constants
CONNECTION_STATUS = {
    'online': 'online',
    'offline': 'offline', 
    'unknown': 'unknown',
    'testing': 'testing'
}

# Diagnostic result constants
DIAGNOSTIC_RESULTS = {
    'success': 'success',
    'warning': 'warning',
    'error': 'error',
    'timeout': 'timeout'
}

# ============================================================================
# SECURITY CONSTANTS
# ============================================================================

# Maximum lengths for validation
MAX_HOSTNAME_LENGTH = 255
MAX_PATH_LENGTH = 4096
MAX_FILENAME_LENGTH = 255

# Allowed characters for validation
ALLOWED_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-."
ALLOWED_PATH_CHARS = ALLOWED_FILENAME_CHARS + "/"

# ============================================================================
# ARCHIVE CONSTANTS
# ============================================================================

# Supported archive formats
SUPPORTED_ARCHIVE_FORMATS = [
    '.zip', '.tar', '.gz', '.tgz', '.bz2', '.xz', 
    '.rar', '.7z', '.tar.gz', '.tar.bz2', '.tar.xz'
]

# Archive extraction paths
EXTRACT_DIR_PREFIX = "extracted_"

# ============================================================================
# SEARCH CONSTANTS
# ============================================================================

# Search options
MAX_SEARCH_RESULTS = 1000
SEARCH_DEPTH_LIMIT = 10

# File type categories
FILE_CATEGORIES = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    'videos': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts', '.m2ts'],
    'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
    'documents': ['.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'],
    'archives': SUPPORTED_ARCHIVE_FORMATS,
    'scripts': ['.sh', '.py', '.pl', '.php', '.js', '.bash'],
    'configs': ['.conf', '.cfg', '.ini', '.xml', '.json', '.yml', '.yaml'],
    'binaries': ['.exe', '.bin', '.so', '.dll', '.out'],
    'text': ['.txt', '.log', '.ini', '.cfg', '.conf', '.xml', '.json', '.yml', '.yaml', '.csv', '.md']
}

# Individual file extension constants (for direct imports)
VIDEO_EXTENSIONS = FILE_CATEGORIES['videos']
IMAGE_EXTENSIONS = FILE_CATEGORIES['images']
AUDIO_EXTENSIONS = FILE_CATEGORIES['audio']
DOCUMENT_EXTENSIONS = FILE_CATEGORIES['documents']
ARCHIVE_EXTENSIONS = FILE_CATEGORIES['archives']
SCRIPT_EXTENSIONS = FILE_CATEGORIES['scripts']
CONFIG_EXTENSIONS = FILE_CATEGORIES['configs']
BINARY_EXTENSIONS = FILE_CATEGORIES['binaries']
TEXT_EXTENSIONS = FILE_CATEGORIES['text']

# ============================================================================
# CACHE CONSTANTS
# ============================================================================

# Cache settings
CACHE_EXPIRY_TIME = 3600  # 1 hour
MAX_CACHE_SIZE = 100 * 1024 * 1024  # 100 MB
CACHE_CLEANUP_INTERVAL = 300  # 5 minutes

# Cache file paths
CACHE_FILE = "/tmp/pilotfs_cache.db"  # Main cache database file
THUMBNAIL_CACHE_DIR = CACHE_DIR + "/thumbnails/"
METADATA_CACHE_FILE = CACHE_DIR + "/metadata.json"

# Cache keys
CACHE_KEYS = {
    'directory_list': 'dir_list_',
    'file_info': 'file_info_',
    'thumbnail': 'thumb_',
    'network_ping': 'ping_',
    'port_scan': 'port_scan_'
}

# ============================================================================
# ERROR CODES
# ============================================================================

# File operation errors
ERROR_CODES = {
    'FILE_NOT_FOUND': 1,
    'PERMISSION_DENIED': 2,
    'DISK_FULL': 3,
    'NETWORK_ERROR': 4,
    'TIMEOUT': 5,
    'INVALID_PATH': 6,
    'UNSUPPORTED_FORMAT': 7,
    'AUTHENTICATION_FAILED': 8,
    'CONNECTION_REFUSED': 9,
    'HOST_UNREACHABLE': 10
}

# ============================================================================
# MISC CONSTANTS
# ============================================================================

# Version information
PLUGIN_VERSION = "2.0.0"
PLUGIN_NAME = "PilotFS"
PLUGIN_DESCRIPTION = "Advanced file manager for Enigma2"

# UI colors (for future theming support)
UI_COLORS = {
    'background': 'background',
    'foreground': 'foreground',
    'selection': 'selection',
    'highlight': 'highlight',
    'warning': 'warning',
    'error': 'error'
}

# Keyboard shortcuts (mapped to Enigma2 keycodes)
KEY_SHORTCUTS = {
    'copy': ['f3', 'c'],
    'move': ['f4', 'm'],
    'delete': ['f8', 'd'],
    'rename': ['f2', 'r'],
    'refresh': ['f5'],
    'tools': ['menu'],
    'context': ['ok_long'],
    'network_tools': ['blue'],
    'quick_ping': ['yellow'],
    'diagnostics': ['red']
}

# ============================================================================
# DEFAULT VALUES
# ============================================================================

# Default paths
DEFAULT_LEFT_PATH = "/media/hdd/"
DEFAULT_RIGHT_PATH = "/"
DEFAULT_STARTING_PANE = "left"

# Default settings
DEFAULT_SHOW_DIRS_FIRST = True
DEFAULT_SORT_MODE = "name"
DEFAULT_TRASH_ENABLED = True
DEFAULT_CACHE_ENABLED = True
DEFAULT_PREVIEW_SIZE = "1024"

# Default network settings
DEFAULT_NETWORK_TIMEOUT = 3
DEFAULT_PING_TIMEOUT = 2
DEFAULT_PORT_SCAN_TIMEOUT = 1
DEFAULT_AUTO_RECONNECT = True
DEFAULT_MAX_RECONNECT_ATTEMPTS = 3
DEFAULT_CONNECTION_CHECK = True
DEFAULT_NETWORK_SCAN_RANGE = "192.168.1"
DEFAULT_REMOTE_IP = "192.168.1.10"

# Default credentials
DEFAULT_FTP_USER = "anonymous"
DEFAULT_FTP_PASS = ""
DEFAULT_SFTP_USER = "root"
DEFAULT_SFTP_PASS = ""