echo "Checking if all packages are up to date"
sudo apt-get update
echo "Installing postgreSQL and postgreSQL-contrib."
sudo apt-get install postgresql postgresql-contrib
echo "Creating the user and database in PostgreSQL"
sudo -u postgres psql -c "CREATE USER guildbot WITH PASSWORD 'gu1ldb0t'; ALTER USER guildbot WITH SUPERUSER; CREATE DATABASE guildbot; \q;"
echo "Installed and established database"
