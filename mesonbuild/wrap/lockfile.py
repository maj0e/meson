# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 The Meson development team

from __future__ import annotations

import os
import typing as T
from dataclasses import dataclass, field

from .. import mlog
from ..mesonlib import MesonException, quiet_git

if T.TYPE_CHECKING:
    from .wrap import PackageDefinition


LOCK_FILE_NAME = 'meson.lock'
LOCK_FILE_VERSION = 1


class LockFileException(MesonException):
    pass


@dataclass
class LockedSubproject:
    """Represents a locked subproject entry."""
    name: str
    type: str  # 'git', 'file', 'hg', 'svn'
    directory: str

    # For git subprojects
    url: T.Optional[str] = None
    revision: T.Optional[str] = None  # From wrap file (branch/tag/commit)
    resolved_commit: T.Optional[str] = None  # Actual resolved commit hash

    # For file subprojects
    source_url: T.Optional[str] = None
    source_filename: T.Optional[str] = None
    source_hash: T.Optional[str] = None

    # For hg subprojects
    hg_url: T.Optional[str] = None
    hg_revision: T.Optional[str] = None

    # For svn subprojects
    svn_url: T.Optional[str] = None
    svn_revision: T.Optional[str] = None

    # Common fields
    patch_url: T.Optional[str] = None
    patch_filename: T.Optional[str] = None
    patch_hash: T.Optional[str] = None

    def to_dict(self) -> T.Dict[str, T.Any]:
        """Convert to dictionary for TOML serialization."""
        result: T.Dict[str, T.Any] = {
            'type': self.type,
            'directory': self.directory,
        }

        if self.type == 'git':
            if self.url:
                result['url'] = self.url
            if self.revision:
                result['revision'] = self.revision
            if self.resolved_commit:
                result['commit'] = self.resolved_commit
        elif self.type == 'file':
            if self.source_url:
                result['source_url'] = self.source_url
            if self.source_filename:
                result['source_filename'] = self.source_filename
            if self.source_hash:
                result['source_hash'] = self.source_hash
        elif self.type == 'hg':
            if self.hg_url:
                result['url'] = self.hg_url
            if self.hg_revision:
                result['revision'] = self.hg_revision
        elif self.type == 'svn':
            if self.svn_url:
                result['url'] = self.svn_url
            if self.svn_revision:
                result['revision'] = self.svn_revision

        # Add patch information if present
        if self.patch_url:
            result['patch_url'] = self.patch_url
        if self.patch_filename:
            result['patch_filename'] = self.patch_filename
        if self.patch_hash:
            result['patch_hash'] = self.patch_hash

        return result

    @staticmethod
    def from_dict(name: str, data: T.Dict[str, T.Any]) -> LockedSubproject:
        """Create from dictionary loaded from TOML."""
        subproject_type = data['type']
        directory = data['directory']

        locked = LockedSubproject(
            name=name,
            type=subproject_type,
            directory=directory,
        )

        if subproject_type == 'git':
            locked.url = data.get('url')
            locked.revision = data.get('revision')
            locked.resolved_commit = data.get('commit')
        elif subproject_type == 'file':
            locked.source_url = data.get('source_url')
            locked.source_filename = data.get('source_filename')
            locked.source_hash = data.get('source_hash')
        elif subproject_type == 'hg':
            locked.hg_url = data.get('url')
            locked.hg_revision = data.get('revision')
        elif subproject_type == 'svn':
            locked.svn_url = data.get('url')
            locked.svn_revision = data.get('revision')

        # Load patch information
        locked.patch_url = data.get('patch_url')
        locked.patch_filename = data.get('patch_filename')
        locked.patch_hash = data.get('patch_hash')

        return locked


@dataclass
class LockFile:
    """Manages the meson.lock file."""
    version: int = LOCK_FILE_VERSION
    subprojects: T.Dict[str, LockedSubproject] = field(default_factory=dict)

    def to_dict(self) -> T.Dict[str, T.Any]:
        """Convert to dictionary for TOML serialization."""
        result: T.Dict[str, T.Any] = {
            'version': self.version,
        }

        if self.subprojects:
            subprojects_list = []
            for name, locked in sorted(self.subprojects.items()):
                entry = locked.to_dict()
                entry['name'] = name
                subprojects_list.append(entry)
            result['subproject'] = subprojects_list

        return result

    def to_toml_string(self) -> str:
        """Convert to TOML string."""
        lines = [f'version = {self.version}', '']

        for name, locked in sorted(self.subprojects.items()):
            lines.append('[[subproject]]')
            lines.append(f'name = "{name}"')
            lines.append(f'type = "{locked.type}"')
            lines.append(f'directory = "{locked.directory}"')

            if locked.type == 'git':
                if locked.url:
                    lines.append(f'url = "{locked.url}"')
                if locked.revision:
                    lines.append(f'revision = "{locked.revision}"')
                if locked.resolved_commit:
                    lines.append(f'commit = "{locked.resolved_commit}"')
            elif locked.type == 'file':
                if locked.source_url:
                    lines.append(f'source_url = "{locked.source_url}"')
                if locked.source_filename:
                    lines.append(f'source_filename = "{locked.source_filename}"')
                if locked.source_hash:
                    lines.append(f'source_hash = "{locked.source_hash}"')
            elif locked.type == 'hg':
                if locked.hg_url:
                    lines.append(f'url = "{locked.hg_url}"')
                if locked.hg_revision:
                    lines.append(f'revision = "{locked.hg_revision}"')
            elif locked.type == 'svn':
                if locked.svn_url:
                    lines.append(f'url = "{locked.svn_url}"')
                if locked.svn_revision:
                    lines.append(f'revision = "{locked.svn_revision}"')

            # Add patch information if present
            if locked.patch_url:
                lines.append(f'patch_url = "{locked.patch_url}"')
            if locked.patch_filename:
                lines.append(f'patch_filename = "{locked.patch_filename}"')
            if locked.patch_hash:
                lines.append(f'patch_hash = "{locked.patch_hash}"')

            lines.append('')

        return '\n'.join(lines)

    @staticmethod
    def from_dict(data: T.Dict[str, T.Any]) -> LockFile:
        """Create from dictionary loaded from TOML."""
        version = data.get('version', 1)
        if version != LOCK_FILE_VERSION:
            raise LockFileException(f'Lock file version {version} is not supported (expected {LOCK_FILE_VERSION})')

        lock_file = LockFile(version=version)

        subprojects_data = data.get('subproject', [])
        for subproject_data in subprojects_data:
            name = subproject_data['name']
            locked = LockedSubproject.from_dict(name, subproject_data)
            lock_file.subprojects[name] = locked

        return lock_file

    @staticmethod
    def from_toml_string(content: str) -> LockFile:
        """Parse TOML string into LockFile."""
        try:
            # Try to use tomllib/tomli for parsing
            from ..cargo.toml import load_toml, TomlImplementationMissing
            import tempfile

            with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
                f.write(content)
                temp_path = f.name

            try:
                data = load_toml(temp_path)
            finally:
                os.unlink(temp_path)

            return LockFile.from_dict(data)
        except (ImportError, TomlImplementationMissing):
            # Fallback: basic TOML parsing for lock files
            return LockFile._parse_toml_basic(content)

    @staticmethod
    def _parse_toml_basic(content: str) -> LockFile:
        """Basic TOML parsing for lock files (fallback)."""
        lines = content.strip().split('\n')
        version = LOCK_FILE_VERSION
        subprojects: T.Dict[str, LockedSubproject] = {}
        current_subproject: T.Optional[T.Dict[str, str]] = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line == '[[subproject]]':
                if current_subproject is not None:
                    if 'name' in current_subproject:
                        name = current_subproject['name']
                        subprojects[name] = LockedSubproject.from_dict(name, current_subproject)
                current_subproject = {}
            elif '=' in line:
                if current_subproject is not None:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"')
                    current_subproject[key] = value
            elif line.startswith('version ='):
                version = int(line.split('=', 1)[1].strip())

        # Add last subproject
        if current_subproject and 'name' in current_subproject:
            name = current_subproject['name']
            subprojects[name] = LockedSubproject.from_dict(name, current_subproject)

        return LockFile(version=version, subprojects=subprojects)

    @staticmethod
    def load(subprojects_dir: str) -> T.Optional[LockFile]:
        """Load lock file from subprojects directory."""
        lock_file_path = os.path.join(subprojects_dir, LOCK_FILE_NAME)
        if not os.path.exists(lock_file_path):
            return None

        try:
            with open(lock_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return LockFile.from_toml_string(content)
        except Exception as e:
            raise LockFileException(f'Failed to load lock file: {e}') from e

    def save(self, subprojects_dir: str) -> None:
        """Save lock file to subprojects directory."""
        lock_file_path = os.path.join(subprojects_dir, LOCK_FILE_NAME)
        content = self.to_toml_string()

        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        mlog.log(f'Lock file saved to {lock_file_path}')

    def add_subproject(self, wrap: PackageDefinition, subproject_dir: str) -> None:
        """Add or update a subproject in the lock file."""
        locked = LockedSubproject(
            name=wrap.name,
            type=wrap.type or 'file',
            directory=wrap.directory,
        )

        if wrap.type == 'git':
            locked.url = wrap.values.get('url')
            locked.revision = wrap.values.get('revision')

            # Try to get the actual resolved commit hash
            repo_path = os.path.join(subproject_dir, wrap.directory)
            if os.path.exists(os.path.join(repo_path, '.git')):
                ret, commit = quiet_git(['rev-parse', 'HEAD'], repo_path)
                if ret:
                    locked.resolved_commit = commit.strip()

        elif wrap.type == 'file':
            locked.source_url = wrap.values.get('source_url')
            locked.source_filename = wrap.values.get('source_filename')
            locked.source_hash = wrap.values.get('source_hash')

        elif wrap.type == 'hg':
            locked.hg_url = wrap.values.get('url')
            locked.hg_revision = wrap.values.get('revision')

        elif wrap.type == 'svn':
            locked.svn_url = wrap.values.get('url')
            locked.svn_revision = wrap.values.get('revision')

        # Add patch information if present
        locked.patch_url = wrap.values.get('patch_url')
        locked.patch_filename = wrap.values.get('patch_filename')
        locked.patch_hash = wrap.values.get('patch_hash')

        self.subprojects[wrap.name] = locked

    def get_subproject(self, name: str) -> T.Optional[LockedSubproject]:
        """Get a locked subproject by name."""
        return self.subprojects.get(name)
