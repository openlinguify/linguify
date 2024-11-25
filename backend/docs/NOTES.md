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

## Project Configuration

### Project Structure
- **`apps` folder**: Contains the Django applications for the project.
- **`settings.py` file**: Main configuration for Django.
- **`docs` folder**: Contains documentation and notes.

### Database Settings
Ensure that the `.env` file contains the correct information for PostgreSQL:
```env
DB_NAME=linguify_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

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

