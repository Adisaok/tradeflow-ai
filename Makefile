.PHONY: up down logs ps
up:
	docker compose up --build
down:
	docker compose down
logs:
	docker compose logs -f --tail=100
ps:
	docker compose ps
