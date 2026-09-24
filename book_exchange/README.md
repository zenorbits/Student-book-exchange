# Book Exchange

A minimalist web application for a student book exchange marketplace. This platform allows students to buy, sell, or exchange their used books easily.

## 🛠 Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite3
- **Frontend:** HTML5, Jinja2 Templates, Bootstrap 5 (CDN), Vanilla JavaScript
- **Security:** Werkzeug (Password Hashing)
- **Deployment:** WSGI ready (Configuration provided for PythonAnywhere)

## ✨ Features

- **User Authentication:** Secure registration, login, and logout functionalities with hashed passwords.
- **Browse & Search Listings:** Browse all available books. Search by title or author, and filter by subject and condition.
- **Dynamic API:** Features an internal API endpoint (`/api/listings`) to fetch book data dynamically in JSON format.
- **Post Advertisements:** Logged-in users can post ads for books, including details like title, author, condition, price, and an image upload.
- **Listing Management:** Users have a dedicated "My Listings" dashboard where they can edit their ads, delete them, or mark them as "Sold".
- **Image Uploads:** Secure image uploading for book covers, stored locally and linked in the database.

## 🚀 How It Works

1. **Database Initialization:** On the first run, the application automatically initializes an SQLite database (`book_exchange.db`) using `schema.sql`. It creates the necessary `users` and `books` tables.
2. **Authentication:** Users must register for an account. Passwords are encrypted before storing. Access to posting and managing ads requires an active session.
3. **Fetching Listings:** The homepage displays available books by calling the `/api/listings` endpoint, which queries the database based on optional search and filter parameters.
4. **Managing Data:** When a user posts a book, it's tied to their `user_id`. Only the owner of a listing can modify or delete it. Uploaded images are secured and saved in the `static/uploads` directory.

## ⚙️ Setup & Run Instructions

### Prerequisites
- Python 3.x installed on your system.

### Installation Steps

1. **Clone or Download the Repository**
2. **Navigate to the Project Directory:**
   ```bash
   cd book_exchange
   ```
3. **Install Dependencies:**
   Install the required Python packages (Flask and Werkzeug).
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application:**
   ```bash
   python app.py
   ```
5. **Access the App:**
   Open your web browser and navigate to `http://127.0.0.1:5000/`.

## 📁 Project Structure

- `app.py`: The main Flask application file containing all routes and logic.
- `database.py`: Helper functions for database connection and initialization.
- `schema.sql`: SQL script defining the database schema for users and books.
- `requirements.txt`: Python dependencies.
- `pythonanywhere_wsgi.py`: WSGI configuration file for deploying on PythonAnywhere.
- `templates/`: Directory containing all HTML/Jinja2 templates.
- `static/`: Directory containing static files like CSS, JS, and user-uploaded images (`static/uploads/`).
