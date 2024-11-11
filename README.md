## Описание


## Запуск

### Создайте файл .env
```bash
touch backend/.env
echo "
DB_HOST=music-postgres
DB_PORT=5432
DB_NAME=store
DB_USER=postgres
DB_PASS=postgres
API_KEY_YOOKASSA=<API_KEY_YOOKASSA>
ID_SHOP_YOOKASSA=<ID_SHOP_YOOKASSA>" > backend/.env
```

### Запустите проект

```bash
docker-compose up -d --build
./database-init.sh
```
