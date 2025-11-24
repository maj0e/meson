# Meson Lock File Usage Example

This document provides practical examples of using the Meson subprojects lock file feature.

## Scenario 1: Starting a New Project with Dependencies

### Step 1: Create your project structure

```bash
mkdir myproject
cd myproject
cat > meson.build <<EOF
project('myproject', 'c')
# Your project code here
EOF

mkdir subprojects
```

### Step 2: Add wrap files for dependencies

```bash
# subprojects/zlib.wrap
cat > subprojects/zlib.wrap <<EOF
[wrap-git]
url = https://github.com/madler/zlib.git
revision = master
EOF
```

### Step 3: Download subprojects

```bash
meson subprojects download
```

This downloads the subprojects based on the wrap files.

### Step 4: Generate lock file

```bash
meson subprojects lock
```

This creates `subprojects/meson.lock` with the exact commit hashes:

```toml
version = 1

[[subproject]]
name = "zlib"
type = "git"
directory = "zlib"
url = "https://github.com/madler/zlib.git"
revision = "master"
commit = "51b7f2abdade71cd9bb0e7a373ef2610ec6f9daf"
```

### Step 5: Commit the lock file

```bash
git add subprojects/meson.lock
git commit -m "Add lock file for reproducible builds"
```

## Scenario 2: Cloning a Project with Lock File

When someone clones your project, they get reproducible builds:

```bash
git clone https://your-repo/myproject.git
cd myproject

# Download subprojects - automatically uses locked commits
meson subprojects download

# Or explicitly instantiate from lock file
meson subprojects instantiate
```

The subprojects will be checked out at the exact commits specified in the lock file.

## Scenario 3: Updating Dependencies

### Update all subprojects

```bash
# This fetches latest from remotes and updates lock file
meson subprojects update --reset

# Verify the changes
git diff subprojects/meson.lock
```

### Update specific subproject

```bash
# Update only zlib
meson subprojects update zlib --reset

# Lock file is automatically updated
```

### Review and commit changes

```bash
git add subprojects/meson.lock
git commit -m "Update zlib to latest version"
```

## Scenario 4: Syncing After Pulling Changes

When you pull changes that updated the lock file:

```bash
git pull

# Sync your local subprojects to match the lock file
meson subprojects instantiate
```

This ensures your local development environment matches the locked versions.

## Scenario 5: Working with Multiple Developers

### Developer A updates a dependency

```bash
cd subprojects/zlib
git pull origin master
cd ../..

# Regenerate lock file with new commit
meson subprojects lock

git commit -am "Update zlib dependency"
git push
```

### Developer B syncs the update

```bash
git pull

# Their local zlib is now outdated
# Instantiate to sync with lock file
meson subprojects instantiate
```

## Scenario 6: Testing Dependency Updates

You want to test a newer version without committing:

```bash
# Update locally
meson subprojects update --reset

# Test your build
meson setup builddir
meson compile -C builddir

# If tests pass, regenerate lock file and commit
meson subprojects lock
git commit -am "Update dependencies"

# If tests fail, revert to locked versions
git restore subprojects/meson.lock
meson subprojects instantiate
```

## Best Practices

### 1. Always commit the lock file

```bash
# Add to git
git add subprojects/meson.lock
git commit -m "Add/update lock file"
```

### 2. Keep lock file in sync

After any `meson subprojects update`, always regenerate the lock file:

```bash
meson subprojects update --reset
# Lock file is automatically updated
git commit -am "Update subprojects"
```

### 3. Use in CI/CD

In your CI pipeline:

```bash
# Ensure reproducible builds
meson subprojects instantiate
meson setup builddir
meson compile -C builddir
meson test -C builddir
```

### 4. Document dependency update process

Create a `CONTRIBUTING.md` with:

```markdown
## Updating Dependencies

1. Update subprojects: `meson subprojects update --reset`
2. Run tests: `meson test -C builddir`
3. Lock file is updated automatically
4. Commit changes: `git commit -am "Update dependencies"`
```

## Common Workflows

### Workflow 1: Fresh checkout

```bash
git clone <repo>
meson subprojects download  # Uses lock file automatically
meson setup builddir
meson compile -C builddir
```

### Workflow 2: Regular development

```bash
# After git pull
meson subprojects instantiate  # Sync to lock file
meson compile -C builddir
```

### Workflow 3: Dependency maintenance

```bash
# Check for updates
meson subprojects update --reset

# Test
meson test -C builddir

# Lock file updated automatically, commit
git commit -am "Update dependencies"
```

## Troubleshooting

### Subproject not at locked version

```bash
# Reset to locked version
meson subprojects instantiate
```

### Lock file out of sync with actual commits

```bash
# Regenerate lock file from current state
meson subprojects lock
```

### Lock file conflicts in git

```bash
# Choose a version
git checkout --theirs subprojects/meson.lock
# Or regenerate
meson subprojects lock
```

## Comparison with Other Systems

### Like Rust's Cargo.lock

- Both record exact dependency versions
- Both are automatically updated on dependency changes
- Both should be committed to version control

### Like npm's package-lock.json

- Ensures reproducible builds across environments
- Resolves dependency graph to specific versions
- Updated alongside dependency changes

### Like Nix's flake.lock

- Provides hermetic builds
- Version-controlled exact dependency snapshots
- Opt-in feature that enhances reproducibility
