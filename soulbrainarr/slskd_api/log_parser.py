from enum import IntEnum
import re
from typing import Optional
from dataclasses import dataclass

@dataclass
class SLSKDError:
    error_message: str

    def __str__(self):
        return self.error_message


class SLSKDUserOfflineError(SLSKDError):
    '''
    Error for when an interaction with a specific user fails because that user isn't online

    Parameters:
        missing_user (Optional[str]): The user that's missing
        message (str): exception message

    '''
    DEFAULT_STR: str = "The user appears to be offline"

    def __init__(self, missing_user: Optional[str] = None, message: str = DEFAULT_STR):
        if missing_user is not None and message == SLSKDUserOfflineError.DEFAULT_STR:
            message = f"The user {missing_user} appears to be offline"
        
        self.missing_user: Optional[str] = missing_user
        super().__init__(message)

class SLSKDNoFilesDownloaded(SLSKDError):
    def __init__(self, message: str = "No files downloaded"):
        super().__init__(message)


def _parse_log_to_user_offline(log: dict) -> Optional[SLSKDUserOfflineError]:
    """
    Returns a set of usernames that triggered a Soulseek.UserOfflineException.
    Example: {"teetime79"}
    """
    error: Optional[SLSKDUserOfflineError] = None
    pattern = re.compile(
        r"User\s+(\S+)\s+appears to be offline", re.IGNORECASE)

    message = log["message"]
    if "Soulseek.UserOfflineException" in message:
        match = pattern.search(message)
        if match:
            error = SLSKDUserOfflineError(missing_user=match.group(1))
        else:
            error = SLSKDUserOfflineError()

    return error

def _parse_log_to_no_download(log: dict) -> Optional[SLSKDNoFilesDownloaded]:
    message = log["message"]
    error: Optional[SLSKDNoFilesDownloaded] = None
    if "Successfully enqueued 0 files from" in message:
        error = SLSKDNoFilesDownloaded()
    return error

def parse_log_to_exception(log: list[dict]) -> Optional[SLSKDError]:
    error = _parse_log_to_user_offline(log)
    if error is not None:
        return error
    
    error = _parse_log_to_no_download(log)
    if error is not None:
        return error
    
    return None
