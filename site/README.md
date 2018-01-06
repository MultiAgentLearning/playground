Steps to run site locally:
1. Set up Postgres. Create a database "playgroud" owned by <username> with <password>.
2. Set in your bash: 
  - `export PLAYGROUND_DATABASE_URL="postgresql://username:password@localhost/playground"`
  - `export PLAYGROUND_SECRET_KEY="falafel"
3. In the module named `a`, run `python manage.py create_db`, `python manage.py db upgrade`, `python manage.py db migrate`. This should build the tables in the database.
4. Then `cd static`, `npm install`.
5. Now to run the back end: `python manage.py runserver`.
6. To start the front end: `cd static`, `npm start`. The homepage will be at `http://localhost:3000`
