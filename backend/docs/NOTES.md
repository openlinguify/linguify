# Backend Documentation

This file contains useful notes and instructions for the backend of the Linguify project.

---

## Table of Contents
1. [Project Configuration](#project-configuration)
2. [Managing Migrations](#managing-migrations)
3. [Bulk Data Import](#bulk-data-import)
4. [Useful Commands](#useful-commands)
5. [Common Issues](#common-issues)

---

## Bootstrap

### Install peotry

Install pipx: https://github.com/pypa/pipx?tab=readme-ov-file#install-pipx

```sh
pipx install poetry
poetry env use 3.12
poetry install
```

More info: https://medium.com/@zalun/django-with-poetry-ea95bd5083f7 

## Project Configuration

### Project Structure
- **`apps` folder**: Contains the Django applications for the project.
- **`settings.py` file**: Main configuration for Django.
- **`docs` folder**: Contains documentation and notes.

### Environment Settings
Ensure that the `.env` file contains the correct information for PostgreSQL and Auth0:
```env
DB_NAME=linguify_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
AUTH0_DOMAIN=YOUR_AUTH0_DOMAIN
AUTH0_CLIENT_ID=YOUR_AUTH0_CLIENT_ID
AUTH0_CLIENT_SECRET=YOUR_AUTH0_CLIENT_SECRET
```
The .env file is available in protonpass under `Project ENV (.env)`

---

## **Step 1: Prepare a CSV File**

Create a CSV file containing the data you want to insert. Make sure that the columns in the file match exactly with the fields of the table in the database.

### Example: `lessons.csv`
```csv
unit_id,lesson_type_id,title,difficulty,estimated_duration,order
1,1,Introduction to Python,Easy,30,1
1,2,Advanced Python,Medium,45,2
2,1,Database Basics,Easy,25,3
2,2,Advanced SQL,Hard,60,4
```

- **`unit_id`**: ID of the associated unit (foreign key).
- **`lesson_type_id`**: ID of the lesson type (foreign key).
- **`title`**: Title of the lesson.
- **`difficulty`**: Difficulty level.
- **`estimated_duration`**: Estimated duration in minutes.
- **`order`**: Order of the lesson within the unit.

---

## **Step 2: Transfer the CSV File to the Server**

The CSV file must be accessible by the PostgreSQL server.

1. Place the file in an accessible directory (e.g., `/tmp/lessons.csv`).
2. If PostgreSQL is on a different server, transfer the file using a tool like `scp`:

   ```bash
   scp lessons.csv user@remote-server:/tmp/lessons.csv
   ```

---

## **Step 3: Connect to PostgreSQL**

Open a PostgreSQL terminal to execute SQL commands.

```bash
psql -U postgres
```

Select the database used by your Django project:

```sql
\c linguify_db
```

---

## **Step 4: Execute the COPY Command**

Use the `COPY` command to insert the data from the CSV file into the PostgreSQL table.

```sql
COPY course_lesson(unit_id, lesson_type_id, title, difficulty, estimated_duration, order)
FROM '/tmp/lessons.csv'
DELIMITER ','
CSV HEADER;
```

### Explanation:
- **`COPY`**: Inserts data directly into the specified table.
- **`FROM '/tmp/lessons.csv'`**: Absolute path to the CSV file on the server.
- **`DELIMITER ','`**: Specifies that columns are separated by commas.
- **`CSV HEADER`**: Indicates that the first line of the file contains column headers.

---

## **Step 5: Verification**

### Verify that the Data Has Been Inserted in PostgreSQL
Run a query to count the number of records in the table:

```sql
SELECT COUNT(*) FROM course_lesson;
```

You can also display the inserted data:

```sql
SELECT * FROM course_lesson LIMIT 10;
```

---

### Verify from Django
1. Open the Django shell:
   ```bash
   python manage.py shell
   ```

2. Test if the data is accessible via Django ORM:
   ```
   python
   from course.models import Lesson
   print(Lesson.objects.count())  # Total number of objects
   lessons = Lesson.objects.all()
   for lesson in lessons[:10]:
       print(lesson.title, lesson.difficulty, lesson.estimated_duration)
   ```

---

## **Step 6: Troubleshooting Common Errors**

1. **Error: Permission Denied**
   - PostgreSQL may not have access to the CSV file. Make sure the PostgreSQL user has permission to read the file.
   - Fix the permissions with:
     ```bash
     chmod 644 /tmp/lessons.csv
     ```

2. **Error: Columns Not Aligned**
   - Ensure that the columns in the CSV file match exactly with the columns expected in the `COPY` command.

3. **Error: Foreign Key Issues**
   - Make sure that the values of `unit_id` and `lesson_type_id` already exist in their respective tables.

---

## **Benefits of the COPY Method**

- **Speed**: COPY is faster than inserting data through Django for large amounts of data.
- **Efficiency**: Useful for data migrations or imports from external systems.

---

With this method, you can efficiently perform bulk data inserts into PostgreSQL.

# tree
find . -type d \( -name "__pycache__" -o -name "migrations" -o -name "venv" \) -prune -o -type f \( -name "*.py" -o -name "requirements.txt" -o -name ".env" \) -print

find . -name "__pycache__" -exec rm -rf {} +


# remove cache of the app
Remove-Item -Recurse -Force -Path "flashcard/__pycache__", "course/__pycache__", "authentication/__pycache__"
Get-ChildItem -Recurse -Force -Include "__pycache__" | Remove-Item -Recurse -Force

# remove all the migrations of the app
Remove-Item -Path "authentication/migrations/*.py" -Exclude "__init__.py"

Remove-Item -Path "chat/migrations/*.py" -Exclude "__init__.py"
Remove-Item -Path "coaching/migrations/*.py" -Exclude "__init__.py"
Remove-Item -Path "community/migrations/*.py" -Exclude "__init__.py"
Remove-Item -Path "course/migrations/*.py" -Exclude "__init__.py"
Remove-Item -Path "data/migrations/*.py" -Exclude "__init__.py"
Remove-Item -Path "flashcard/migrations/*.py" -Exclude "__init__.py"
Remove-Item -Path "payments/migrations/*.py" -Exclude "__init__.py"
Remove-Item -Path "quiz/migrations/*.py" -Exclude "__init__.py"
Remove-Item -Path "revision/migrations/*.py" -Exclude "__init__.py"
Remove-Item -Path "cards/migrations/*.py" -Exclude "__init__.py"


rm -rf authentication/migrations/*.py
rm -rf course/migrations/*.py
rm -rf quiz/migrations/*.py


# make the makemigrations and migrate of the classes

python manage.py makemigrations authentication

python manage.py makemigrations course


# Start the development server
npm start

# Useful commands for the frontend

# Create a new React app
npx create-react-app app_name

# Start the development server
npm start

# Run tests
npm run test

# Create an optimized production build
npm run build

# Remove the single build dependency from your project
npm run eject

# Fix vulnerabilities in the dependencies
npm audit fix --force


##### Useful commands for the backend ###########
# Create a new virtual environment
.\venv\Scripts\Activate

# Install Django
pip install django

# Install Django REST framework

pip install djangorestframework

# Create a new Django project
django-admin startproject project_name

# Create a new Django app
python manage.py startapp app_name

# Run the development server
python manage.py runserver

# Create a new Django superuser

python manage.py createsuperuser

# Create database migrations

python manage.py makemigrations

# Apply database migrations

python manage.py migrate

# Run tests

python manage.py test

# Create a new Django app with a custom user model

python manage.py startapp app_name

# Generate Django models from an existing database
python manage.py inspectdb > app_name/models.py

# Install the Django REST framework package
pip install djangorestframework

# Freeze the current state of the installed packages and save it to requirements.txt
pip freeze > requirements.txt
