build:
	docker-compose build

run:
	docker-compose up

stop:
	docker-compose stop

restart:
	docker-compose restart

logs:
	docker-compose logs

remove:
	docker-compose rm --force -v

run: build run

clean: stop remove