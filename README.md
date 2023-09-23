### Installation

1. Clone project using command `git clone git@github.com:insideItself/404state_key_storage.git`
2. Create `.env`-file in main project directory that will contain project credentials. Use file `.env.EXAMPLE` as example.
3. Run project using command `docker-compose up -d --build --scale app=3`

### Project Schema

1. User press 'Connect' button in Outline app. Outline app sends HTTPS request to NGINX-server.
2. After receiving request from Outline client, NGINX sends HTTPS request to one of gunicorn web-servers.
3. Gunicorn using WSGI sends HTTPS request to flask-app. Request contains user UUID.
4. Flask-app using user UUID sends request to Postgres database to find the following data:
   * vpn-server hostname
   * vpn-server port
   * user password
   * encryption method
5. After the data has been successfully retrieved from the database, flask-app creates json-file and sends it back to user Outline app through HTTPS.
6. Outline client connect user to vpn-server using credentials from json-file.

![database_schema](docs/schema.jpg)