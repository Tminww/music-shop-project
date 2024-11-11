until docker exec -i biologic-postgres pg_isready -U postgres; do
    echo "Ждем, пока PostgreSQL станет доступным..."
    sleep 2
done

docker exec -i music-backend python /web_django/manage.py migrate
docker exec -i music-backend python /web_django/manage.py loaddata /web_django/db.json
