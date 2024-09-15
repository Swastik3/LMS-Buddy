# Name of the running container
$CONTAINER_NAME = "iris-comm"

# Name for the new image
$NEW_IMAGE_NAME = "my-iris-community"

# Tag for the new image
$IMAGE_TAG = "v1"

# Verify the container is running
Write-Host "Verifying container is running:"
docker ps | Select-String $CONTAINER_NAME

# Commit the container to a new image
docker commit $CONTAINER_NAME "${NEW_IMAGE_NAME}:${IMAGE_TAG}"

# Verify the new image was created
Write-Host "New image created:"
docker images | Select-String $NEW_IMAGE_NAME