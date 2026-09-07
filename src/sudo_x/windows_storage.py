"""Windows private storage and exclusive launcher lease (no shell commands)."""

import stat
from pathlib import Path

import ntsecuritycon
import pywintypes
import win32api
import win32con
import win32file
import win32security


def current_user():
    token = win32security.OpenProcessToken(
        win32api.GetCurrentProcess(), win32con.TOKEN_QUERY
    )
    try:
        return win32security.GetTokenInformation(token, win32security.TokenUser)[0]
    finally:
        token.Close()


def assert_private(path: Path, handle=None) -> None:
    """Reject reparse points, foreign owners, and grants outside user/system/admins."""
    info = path.lstat()
    if info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        raise ValueError("SUDO X storage must be non-symlink and non-junction.")
    query = win32security.GetNamedSecurityInfo if handle is None else win32security.GetSecurityInfo
    descriptor = query(
        str(path) if handle is None else handle, win32security.SE_FILE_OBJECT,
        win32security.OWNER_SECURITY_INFORMATION | win32security.DACL_SECURITY_INFORMATION,
    )
    user = current_user()
    if descriptor.GetSecurityDescriptorOwner() != user:
        raise ValueError("SUDO X storage must be user-owned.")
    allowed = {
        win32security.ConvertSidToStringSid(user), "S-1-5-18", "S-1-5-32-544", "S-1-3-4",
    }
    dacl = descriptor.GetSecurityDescriptorDacl()
    if dacl is None or dacl.GetAceCount() == 0:
        raise ValueError("SUDO X storage requires a private Windows ACL.")
    for index in range(dacl.GetAceCount()):
        ace = dacl.GetAce(index)
        if ace[0][0] == win32security.ACCESS_DENIED_ACE_TYPE:
            continue
        if (
            ace[0][0] != win32security.ACCESS_ALLOWED_ACE_TYPE
            or win32security.ConvertSidToStringSid(ace[2]) not in allowed
        ):
            raise ValueError("SUDO X storage requires a private Windows ACL.")


def prepare_directory(directory: Path) -> None:
    if not directory.exists():
        directory.parent.mkdir(parents=True, exist_ok=True)
        user = current_user()
        dacl = win32security.ACL()
        flags = win32con.OBJECT_INHERIT_ACE | win32con.CONTAINER_INHERIT_ACE
        for sid in (user, win32security.ConvertStringSidToSid("S-1-5-18"),
                    win32security.ConvertStringSidToSid("S-1-5-32-544")):
            dacl.AddAccessAllowedAceEx(
                win32security.ACL_REVISION, flags, ntsecuritycon.FILE_ALL_ACCESS, sid
            )
        security = pywintypes.SECURITY_ATTRIBUTES()
        security.SECURITY_DESCRIPTOR.SetSecurityDescriptorOwner(user, False)
        security.SECURITY_DESCRIPTOR.SetSecurityDescriptorDacl(True, dacl, False)
        security.SECURITY_DESCRIPTOR.SetSecurityDescriptorControl(
            win32security.SE_DACL_PROTECTED, win32security.SE_DACL_PROTECTED
        )
        win32file.CreateDirectory(str(directory), security)
    if not directory.is_dir():
        raise ValueError("SUDO X data directory must be a directory.")
    assert_private(directory)


def acquire_lease(directory: Path):
    path = directory / "session.lock"
    try:
        handle = win32file.CreateFile(
            str(path), win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            0, None, win32con.OPEN_ALWAYS,
            win32file.FILE_FLAG_OPEN_REPARSE_POINT, None,
        )
    except pywintypes.error as exc:
        if exc.winerror == 32:
            raise ValueError("Another SUDO X process is using this data directory.") from exc
        raise
    try:
        assert_private(path, handle)
        if path.stat().st_nlink != 1:
            raise ValueError("SUDO X lock must not be hard-linked.")
    except BaseException:
        handle.Close()
        raise
    return handle
