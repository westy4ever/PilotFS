class PilotFSError(Exception):
    """Base exception for PilotFS"""
    pass

class FileOperationError(PilotFSError):
    """File operation failed"""
    pass

class NetworkError(PilotFSError):
    """Network operation failed"""
    pass

class PermissionError(PilotFSError):
    """Permission denied"""
    pass

class DiskSpaceError(PilotFSError):
    """Insufficient disk space"""
    pass

class CacheError(PilotFSError):
    """Cache operation failed"""
    pass

class RemoteConnectionError(PilotFSError):
    """Remote connection failed"""
    pass

class InvalidInputError(PilotFSError):
    """Invalid user input"""
    pass

class ArchiveError(PilotFSError):
    """Archive operation failed"""
    pass

class MediaPlaybackError(PilotFSError):
    """Media playback failed"""
    pass