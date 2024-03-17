kill:
	docker kill sps
	docker container prune -f

run:
	docker build -t sps .
	docker run --restart always -dp 5000:5000 --name sps sps