# Apply database migrations

python manage.py collectstatic --noinput
echo "Apply database migrations"
python manage.py makemigrations
python manage.py migrate

echo "Creating Superuser"
python manage.py init

# Start server
echo "Starting server"
daphne -b 0.0.0.0 -p 8000 core.asgi:application
