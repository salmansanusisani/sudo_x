"""Exercise real Windows ACLs, hard links, and launcher lease release."""

import os

import pytest

from sudo_x.store import Store

pytestmark = pytest.mark.skipif(os.name != "nt", reason="Windows ACL tests")


def grant_everyone(path):
    import ntsecuritycon
    import win32security

    descriptor = win32security.GetNamedSecurityInfo(
        str(path), win32security.SE_FILE_OBJECT, win32security.DACL_SECURITY_INFORMATION
    )
    acl = descriptor.GetSecurityDescriptorDacl()
    acl.AddAccessAllowedAce(
        win32security.ACL_REVISION, ntsecuritycon.FILE_GENERIC_READ,
        win32security.ConvertStringSidToSid("S-1-1-0"),
    )
    win32security.SetNamedSecurityInfo(
        str(path), win32security.SE_FILE_OBJECT,
        win32security.DACL_SECURITY_INFORMATION, None, None, acl, None,
    )


def test_rejects_public_directory(tmp_path):
    directory = tmp_path / "data"
    Store(directory).close()
    grant_everyone(directory)
    with pytest.raises(ValueError, match="private Windows ACL"):
        Store(directory)


def test_rejects_public_database_and_releases_lease(tmp_path):
    import win32security

    directory = tmp_path / "data"
    Store(directory).close()
    database = directory / "tasks.sqlite3"
    original = win32security.GetNamedSecurityInfo(
        str(database), win32security.SE_FILE_OBJECT, win32security.DACL_SECURITY_INFORMATION
    ).GetSecurityDescriptorDacl()
    grant_everyone(database)
    with pytest.raises(ValueError, match="private Windows ACL"):
        Store(directory)
    win32security.SetNamedSecurityInfo(
        str(database), win32security.SE_FILE_OBJECT,
        win32security.DACL_SECURITY_INFORMATION, None, None, original, None,
    )
    Store(directory).close()


def test_rejects_hard_linked_database(tmp_path):
    directory = tmp_path / "data"
    Store(directory).close()
    (tmp_path / "alias.sqlite3").hardlink_to(directory / "tasks.sqlite3")
    with pytest.raises(ValueError, match="private regular file"):
        Store(directory)


def test_rejects_reparse_point(tmp_path, monkeypatch):
    import stat
    from types import SimpleNamespace

    from sudo_x.windows_storage import assert_private

    # Simulate lstat's reparse flag without requiring administrator symlink privileges.
    monkeypatch.setattr(type(tmp_path), "lstat", lambda self: SimpleNamespace(
        st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT
    ))
    with pytest.raises(ValueError, match="non-junction"):
        assert_private(tmp_path)
