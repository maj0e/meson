# Meson Subprojects Lock File Implementation

## Summary

This implementation adds a lock file feature for Meson subprojects, similar to Rust's `cargo.lock` or Nix's `flake.lock`. This allows for reproducible builds without requiring version pinning in wrap files.

## Files Created

### mesonbuild/wrap/lockfile.py
New module containing:
- `LockedSubproject`: Data class representing a locked subproject entry
- `LockFile`: Manager class for the lock file
- TOML serialization/deserialization support
- Methods to add/get subprojects from lock file

## Files Modified

### mesonbuild/wrap/wrap.py
Changes:
- Added import for `LockFile` and `LockedSubproject`
- Added `lockfile` field to `Resolver` class
- Added `load_lockfile()` method to load lock file during initialization
- Modified `_get_git()` to use locked commit if available

### mesonbuild/msubprojects.py
Changes:
- Added import for `LockFile`
- Added `gen_lock()` method to `Runner` class
- Added `instantiate()` method to `Runner` class
- Added `run_lock_post()` function for lock file generation
- Added command-line parsers for `lock` and `instantiate` commands
- Modified `run()` to automatically update lock file after `update` command if lock file exists

### unittests/subprojectscommandtests.py
Changes:
- Added `test_lock_file()` test case that:
  - Creates a git subproject
  - Generates a lock file
  - Verifies lock file format and contents
  - Tests the instantiate command

### docs/markdown/Wrap-dependency-system-manual.md
Changes:
- Added comprehensive documentation section "Lock file for reproducible builds"
- Documented lock file format
- Documented new commands: `meson subprojects lock` and `meson subprojects instantiate`
- Explained behavior and usage patterns

## Lock File Format

The lock file is stored at `subprojects/meson.lock` in TOML format:

```toml
version = 1

[[subproject]]
name = "subproject-name"
type = "git"
directory = "subproject-directory"
url = "https://github.com/user/repo"
revision = "main"
commit = "full-40-char-commit-hash"
```

Additional fields for different subproject types:
- **git**: `url`, `revision`, `commit`
- **file**: `source_url`, `source_filename`, `source_hash`
- **hg**: `url`, `revision`
- **svn**: `url`, `revision`
- All types can have: `patch_url`, `patch_filename`, `patch_hash`

## New Commands

### meson subprojects lock

Generates a lock file from currently downloaded subprojects:

```bash
meson subprojects lock
```

This command:
1. Scans all wrap files in the subprojects directory
2. For each downloaded git subproject, records the current commit hash
3. Saves the information to `subprojects/meson.lock`

### meson subprojects instantiate

Checks out subprojects at versions specified in the lock file:

```bash
meson subprojects instantiate
```

This command:
1. Reads the lock file
2. For each git subproject, checks out the locked commit
3. Useful after pulling changes that updated the lock file

## Behavior

### Opt-in Feature
- If no `meson.lock` file exists, behavior is unchanged
- The lock file is created explicitly via `meson subprojects lock`

### Automatic Lock File Usage
- When downloading/cloning subprojects, if a lock file exists, the locked commit is used
- `meson subprojects update` automatically updates the lock file if it exists

### Subproject Lock Files
- Only the main project's lock file is used
- Lock files in subprojects themselves are ignored

## Implementation Details

### Lock File Loading
- Lock file is loaded during `Resolver.__post_init__()`
- Failures to load are logged as warnings but don't stop execution
- Uses Python's `tomllib` (3.11+) or `tomli` module for parsing

### Git Integration
- In `_get_git()`, checks lock file for resolved commit before cloning
- Uses full 40-character commit hashes for reproducibility
- Falls back to wrap file revision if no lock file entry exists

### TOML Generation
- Lock file is generated in sorted order for consistency
- Simple TOML generation without external dependencies (for writing)
- Falls back to basic TOML parsing if tomllib/tomli not available

## Testing

A comprehensive test (`test_lock_file`) covers:
1. Lock file generation
2. Lock file format validation
3. Instantiate command functionality
4. Integration with update command

## Benefits

1. **Reproducible Builds**: Exact commit hashes ensure identical builds
2. **No Version Pinning**: Wrap files can use branches/tags without lock-in
3. **Flexible Updates**: Easy to update dependencies and re-lock
4. **Git-Friendly**: Lock file can be committed to version control
5. **Compatible**: Opt-in design means existing projects unchanged

## Future Enhancements

Potential improvements for future versions:
- Support for resolving hashes for file/hg/svn subprojects
- Checksum verification for downloaded files
- Lock file validation commands
- Automatic lock file updates on subproject changes
- Integration with CI/CD systems
