build:
	docker-compose build

up:
	docker-compose up -d

stop:
	docker-compose stop

restart:
	docker-compose restart

logs:
	docker-compose logs

remove:
	docker-compose rm --force -v

run: build up

clean: stop remove