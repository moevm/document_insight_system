COMMIT=$(git rev-parse HEAD)
COMMIT_MSG=$(git log --format=%B -n 1 $COMMIT)
DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VERSION=$(git tag | tail -1)
# VERSION_FILE_PATH="$(dirname $(dirname $(readlink -f $0)))/$VERSION_FILE_NAME"
# echo $VERSION_FILE_PATH
[ ${#VERSION} == 0 ] && VERSION="no version" 
echo "{
\"commit\":  \"$COMMIT\",
\"message\":  \"$COMMIT_MSG\",
\"date\":    \"$DATE\",
\"version\": \"$VERSION\"
}"