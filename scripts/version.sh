COMMIT=$(git rev-parse HEAD)
DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VERSION=$(git tag | tail -1)
# VERSION_FILE_PATH="$(dirname $(dirname $(readlink -f $0)))/$VERSION_FILE_NAME"
# echo $VERSION_FILE_PATH
[ ${#VERSION} == 0 ] && VERSION="no version" 
echo "{ 
\"commit\":  \"$COMMIT\",
\"date\":    \"$DATE\",
\"version\": \"$VERSION\"
}"