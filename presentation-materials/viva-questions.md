# Viva Questions and Answers

## 20 Project Viva Questions

1. **What is Smart Lost & Found Portal?**  It is a web application for reporting, searching, and claiming lost or found campus items.
2. **Why did you choose this project?**  Lost items are a common college problem and the project has a clear real-world use.
3. **Who are the users?**  Students and an administrator.
4. **What is the main benefit?**  It keeps all reports in one searchable place.
5. **What can a student report?**  A lost item or a found item with details, date, location, contact number, and an optional image.
6. **How is a claim handled?**  A user submits a reason and the administrator approves or rejects it.
7. **Why is admin approval needed?**  It helps reduce false claims.
8. **What pages does the system have?**  Home, Login, Dashboard, Report Lost Item, Browse Items, and Admin Panel.
9. **What information is shown in browsing?**  Item name, category, type, description, date, location, and status.
10. **How can users find items faster?**  They can search by keyword and filter by category or availability.
11. **What does the dashboard show?**  Counts of lost, found, open, and claimed items plus recent reports.
12. **What happens after a claim is approved?**  The claim becomes approved and the item is marked claimed.
13. **Can an administrator remove reports?**  Yes, fake or inappropriate reports can be deleted.
14. **Why did you add image upload?**  Photos make item identification easier.
15. **Is the project responsive?**  Yes, Streamlit columns and custom CSS adapt to available screen size.
16. **What are the main tables?**  Users, Items, and Claims.
17. **What data is stored in Items?**  Item details, report type, location, date, image path, contact number, and status.
18. **How does login work?**  The application verifies the username and hashed password against the Users table.
19. **What is the limitation of this version?**  SQLite data on Community Cloud may reset because storage is temporary.
20. **What future improvements are possible?**  Notifications, automatic matching, registration, QR codes, and a cloud database.

## 20 Technical Questions and Answers

1. **What is Streamlit?**  It is a Python framework for building interactive web applications quickly.
2. **Why use Python?**  It is readable, productive, and integrates well with Streamlit and SQLite.
3. **What is SQLite?**  It is a lightweight relational database stored in one local file.
4. **Why choose SQLite?**  It requires no separate server and is perfect for a simple demonstration project.
5. **What is a primary key?**  A unique value that identifies each row, such as `id`.
6. **What is a foreign key?**  A field that links a row to another table, for example `items.user_id` linking to Users.
7. **How are passwords stored?**  They are converted to a SHA-256 hash before being stored.
8. **What is session state?**  Streamlit session state stores temporary data for one user session, such as the logged-in user ID.
9. **What is CRUD?**  Create, Read, Update, and Delete operations on data.
10. **Where is CRUD used here?**  Reports are created/read/deleted, and claims are created/read/updated.
11. **How does filtering work?**  SQL WHERE conditions are added based on the selected category and status.
12. **How does search work?**  SQL LIKE queries check the item name, description, and location.
13. **Why use parameterized SQL queries?**  They safely pass values and help prevent SQL injection.
14. **What is `check_same_thread=False` used for?**  It allows the SQLite connection setup to work safely with Streamlit’s execution pattern.
15. **What does `IF NOT EXISTS` do?**  It creates a table only if it has not already been created.
16. **How is an uploaded image saved?**  It is written to `assets/uploads` with a unique UUID-based filename.
17. **What is a UUID?**  A highly unique identifier used here to prevent filename conflicts.
18. **What is role-based access control?**  Access is restricted based on user role; only admins can use the Admin Panel.
19. **What is deployment?**  It is publishing an application so users can access it online.
20. **Why is Streamlit Community Cloud suitable?**  It is simple, free for public demos, and deploys directly from GitHub.
