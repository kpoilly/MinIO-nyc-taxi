#!/bin/bash

# Wait for MinIO to be fully ready before configuring mc
echo "Waiting for MinIO to be fully ready..."
sleep 10

# Set MinIO client alias for 'myminio'
mc alias set myminio http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# Optionally, set the default bucket alias (if you have a default bucket)
mc alias set default http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# You can add more mc configurations if needed

echo "MinIO Client (mc) setup complete!"
