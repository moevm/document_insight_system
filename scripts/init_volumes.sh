#!/bin/sh
set -eu

# Run only in the root init service, before any application writers start.
# Do not follow symlinks or descend into other mounted filesystems.
for volume in "$@"; do
    if [ ! -d "$volume" ] || [ -L "$volume" ]; then
        echo "Expected a volume directory: $volume" >&2
        exit 1
    fi
    find "$volume" -xdev -exec chown -h app:app {} +
    find "$volume" -xdev -type d -exec chmod u+rwx {} +
    find "$volume" -xdev -type f -exec chmod u+rw {} +
done
