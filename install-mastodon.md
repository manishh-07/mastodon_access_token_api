I'm assuming you're running the latest version of Ubuntu (24.04) or Debian (12), so the installation of prerequisites will use apt.
1. Login as root: `sudo -i`
2. Install the prerequisites: `apt install docker.io docker-compose nginx python3-venv`
3. Create directory for Mastodon: `mkdir /opt/mastodon`
4. Enter to Mastodon directory: `cd /opt/mastodon`
5. Create directory for Postgres: `mkdir postgres14`
6. Create directory for Redis: `mkdir redis`
7. Create directory for Mastodon files: `mkdir -p public/system`
8. Set owner to Mastodon user (991) for public directory: `chown -R 991:991 public`
9. Get docker-compose.yml for Mastodon: `wget https://raw.githubusercontent.com/mastodon/mastodon/main/docker-compose.yml`
10. Edit docker-compose.yml in a text editor to comment out `build` lines:

![Screenshot_3](https://gist.github.com/assets/159741417/737600c0-a6c4-41eb-88fe-cc7494534bdb)

![Screenshot_5](https://gist.github.com/assets/159741417/f5eb8db3-078b-4a54-9412-115694d3f33e)

![Screenshot_6](https://gist.github.com/assets/159741417/dd89744f-bde9-4aec-9c46-7b4b86b47ba5)

11. Generate a password for postgres database: `openssl rand -hex 12`
12. Copy the generated password to another place.
13. Deploy postgres container: `docker run --rm --name postgres -v $PWD/postgres14:/var/lib/postgresql/data -e POSTGRES_PASSWORD="opensslgen" -d postgres:14-alpine` (with "opensslgen" being the password you generate earlier.)
14. Enter psql prompt: `docker exec -it postgres psql -U postgres`
15. Create database for Mastodon: `CREATE USER mastodon WITH PASSWORD 'opensslgen' CREATEDB;` (with "opensslgen" being the password you generate earlier.)
16. Exit from psql prompt: `exit`
17. Stop postgres container: `docker stop postgres`
18. Create .env.production file: `touch .env.production`
19. Start Mastodon setup wizard: `docker-compose run --rm web bundle exec rake mastodon:setup`
20. Answer the questions:
```
Domain name: mastodon.example.com

Single user mode disables registrations and redirects the landing page to your public profile.
Do you want to enable single user mode? yes

Are you using Docker to run Mastodon? Yes

PostgreSQL host: db
PostgreSQL port: 5432
Name of PostgreSQL database: mastodon
Name of PostgreSQL user: mastodon
Password of PostgreSQL user:
Database configuration works! 🎆

Redis host: redis
Redis port: 6379
Redis password:
Redis configuration works! 🎆

Do you want to store uploaded files on the cloud? No

Do you want to send e-mails from localhost? No
SMTP server: smtp.example.com
SMTP port: 587
SMTP username: smtp@example.com
SMTP password:
SMTP authentication: plain
SMTP OpenSSL verify mode: none
Enable STARTTLS: auto
E-mail address to send e-mails "from": Mastodon <notifications@mastodon.example.com>
Send a test e-mail with this configuration right now? no

Do you want Mastodon to periodically check for important updates and notify you? (Recommended) Yes

This configuration will be written to .env.production
Save configuration? Yes
```
21. Before answering yes to "prepare database now?" question, copy the generated .env.production above to somewhere else.
22. Continue answering questions:
```
Now that configuration is saved, the database schema must be loaded.
If the database already exists, this will erase its contents.
Prepare the database now? Yes
Running `RAILS_ENV=production rails db:setup` ...


Created database 'mastodon'
Done!

All done! You can now power on the Mastodon server 🐘

Do you want to create an admin user straight away? no
```
> Why not create the admin user? Because in my testing, either web container unable to contact redis or UniqueViolation error will occur if you say yes, and admin user won't have a password.
23. Paste .env.production you copied earlier to `/opt/mastodon/.env.production`
24. Create admin user for Mastodon: `docker-compose run --rm web tootctl accounts create example --email email@example.com --confirmed --role Owner`
25. Save your password set for your Mastodon account. Now start Mastodon with `docker-compose up -d`

Congrats for completing Mastodon part of this tutorial! Let's configure nginx.

26. Install certbot with these commands:
```
python3 -m venv /opt/certbot
/opt/certbot/bin/pip install --upgrade pip
/opt/certbot/bin/pip install certbot certbot-nginx
```
27. For issuing SSL certificate, we need a temporary vhost. Create the directory for it: `mkdir /var/www/mastodon`
28. Create an index.html: `echo hello world >> /var/www/mastodon/index.html`
29. Insert this to `/etc/nginx/conf.d/mastodon.conf`:
```
server {
server_name mastodon.example.com;
listen 80;
root /var/www/mastodon;
}
```
30. Reload nginx: `systemctl reload nginx`
31. Obtain SSL certificate for Mastodon: `/opt/certbot/bin/certbot --nginx -d mastodon.example.com`
32. Delete the temporary vhost: `rm /etc/nginx/conf.d/mastodon.conf`
33. Delete temporary vhost's directory: `rm /var/www/mastodon`
34. Download the pre-made nginx config file for Mastodon: `wget -O /etc/nginx/conf.d/mastodon.conf https://raw.githubusercontent.com/mastodon/mastodon/main/dist/nginx.conf`
35. Edit `/etc/nginx/conf.d/mastodon.conf` to replace:
```
A. /home/mastodon/live/public with /opt/mastodon/public
B. example.com with your Mastodon domain.
C. Uncomment ssl_certificate and ssl_certificate_key lines and replace example.com with your Mastodon domain.
D. Replace =404 with @proxy
```
36. Reload nginx again: `systemctl reload nginx`
37. Visit your Mastodon domain, login to your admin account, and you'll see that your own account is pending approval. Approve yourself with `docker-compose run --rm web tootctl accounts approve --all`
38. We're done! Enjoy tooting!