# FastAPI-MongoDB CRUD Starter

## Introduction

## Getting Started

To launch the project, run the following command:

```bash
docker compose up -d --build
```

This command will build and start all necessary containers in detached mode.

## CRUD Testing

You can test the CRUD operations using Postman. For example, to create a new item:

1. Set the HTTP method to **POST**.
2. Select **Body > Raw > JSON**.
3. Use the endpoint: `http://localhost:8000/items/`.
4. Provide the following JSON in the request body:

    ```json
    {
        "name": "Example Item",
        "description": "This is a test item"
    }
    ```

## Backup and Restore

### Automatic Backup

Database backups run at 4 AM daily. The system retains a maximum of 3 backup files.

### Manual Backup

To perform a manual backup, execute:

```bash
docker exec -it mongodb bash -c 'mongodump --archive=/data/backup/backup_$(date +%Y%m%d_%H%M%S).gz --gzip'
```

### Manual Restore

To restore from a backup, run the following command (replace the timestamp with the desired backup file):

```bash
docker exec -it mongodb bash -c 'mongorestore --drop --archive=/data/backup/backup_20250319_040000.gz --gzip'
```

## File Structure

```
.
├── docker-compose.yml
├── crud
│   ├── Dockerfile
│   └── crud.py
├── backup
│   ├── Dockerfile
│   └── backup.py
└── mongo_backupds   # Directory on the host where backup files are stored
```

The structure separates the CRUD API and backup scripts into their respective directories and includes the Docker Compose configuration for easy deployment.
