echo "Checking if all packages are up to date"
sudo apt-get update
sudo apt-get upgrade
echo "Installing postgreSQL and postgreSQL-contrib"
sudo apt-get install postgresql postgresql-contrib
echo "Starting postgres server in case of it being offline"
sudo service postgresql start
echo "Creating the user and database"
sudo -u postgres psql -c "CREATE USER guildbot WITH PASSWORD 'gu1ldb0t';" -c "CREATE DATABASE guildbot;"
echo "Installed and established database and user. Finished!"
