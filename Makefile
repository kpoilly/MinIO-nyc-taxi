docker-minio:
	docker run -p 9000:9000 -p 9001:9001 datascientest/minio server /data --console-address ":9001"

docker--minio-secure:
	docker run -p 9000:9000 -p 9001:9001 -v /data:/data -e MINIO_ROOT_USER=username -e MINIO_ROOT_PASSWORD=password datascientest/minio server /data --console-address ":9001"

install-client:
	wget https://dl.min.io/client/mc/release/linux-amd64/mc
	chmod +x mc
	sudo mv mc /usr/local/bin/

mc-alias:
	mc alias set docker_minio http://127.0.0.1:9000 minioadmin minioadmin
	@# mc alias set docker_minio http://127.0.0.1:9000 yourusername yourpassword

info:
	mc admin info docker_minio

add-bucket1:
	touch data.csv
	mc mb docker_minio/bucket1
	mc cp ./data.csv docker_minio/bucket1
	mc ls docker_minio/bucket1

add-bucket2:
	mc mb docker_minio/bucket2
	mc cp docker_minio/bucket1/data.csv docker_minio/bucket2
	mc ls docker_minio/bucket2

list-buckets:
	mc ls docker_minio
	
rm-bucket1:
	mc rb docker_minio/bucket1 --force

rm-bucket2:
	mc rb docker_minio/bucket2 --force

add-user1:
	mc admin user add docker_minio user1 password123

disable-user1:
	mc admin user disable docker_minio user1

enable-user1:
	mc admin user enable docker_minio user1

info-user1:
	mc admin user info docker_minio user1

list-users:
	mc admin user ls docker_minio

set-venv:
	@# pip install uv
	python3 -m uv venv
	source .venv/bin/activate
	pip install -r requirements.txt

docker-minio-mlflow:
	docker-compose up --build -d

ingest-data:
	python src/data/data_ingestion.py

.PHONY:
	run-docker run-docker-secure install-client mc-alias info add-bucket1 add-bucket2\
	list-buckets rm-bucket1 rm-bucket2 add-user1 disable-user1 enable-user1 info-user1\
	list-users set-venv docker-minio-mlflow ingest-data
 