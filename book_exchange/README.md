# Student Book Exchange

A minimalist, yet powerful web application built to facilitate a student book exchange marketplace. This platform empowers students to buy, sell, or exchange their used academic and non-academic books with ease.

## 🚀 Features

- **User Authentication:** Secure registration, login, and logout functionalities with hashed passwords (using Werkzeug).
- **Email Verification (OTP):** Two-factor style email verification during registration to ensure genuine student accounts.
- **Marketplace Browsing & Search:** Browse all available books. Search by title or author, and filter by subject and condition to find exactly what you need.
- **Dynamic Internal API:** Features an internal API endpoint (`/api/listings`) to fetch and display book data dynamically in JSON format.
- **Ad Posting & Image Uploads:** Authenticated users can post advertisements for books, including details like title, author, condition, price, and secure image uploads for book covers.
- **Listing Management:** Dedicated "My Listings" dashboard for users to manage, edit, mark as "Sold", or delete their posted advertisements.
- **Real-time Interaction:** Connect with other students to negotiate and finalize book exchanges.

## 🛠 Tech Stack

- **Backend:** Python 3, Flask
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Jinja2 Templates, Bootstrap 5 (CDN)
- **Security & Utilities:** 
  - Werkzeug (Password Hashing, Secure Filenames)
  - `python-dotenv` for environment variable management
  - `smtplib` for email OTP delivery
- **Deployment:** WSGI ready (Configuration provided for platforms like PythonAnywhere)

## ⚙️ Setup & Run Instructions

### Prerequisites
- Python 3.8+ installed on your system.

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <your-repository-url>
   cd book_exchange
   ```

2. **Set up a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your SMTP configurations for OTP emails:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

5. **Initialize and Run the Application:**
   On the first run, the app will automatically initialize the SQLite database (`book_exchange.db`).
   ```bash
   python app.py
   ```

6. **Access the App:**
   Open your web browser and navigate to `http://127.0.0.1:5000/`.

## 📁 Project Structure

- `app.py`: The main Flask application file containing all routes, business logic, and API endpoints.
- `database.py`: Helper functions for database connection and initialization.
- `schema.sql`: SQL script defining the database schema for users and books.
- `requirements.txt`: Project dependencies and libraries.
- `pythonanywhere_wsgi.py`: WSGI configuration file for seamless deployment.
- `templates/`: Directory containing all HTML views and Jinja2 templates.
- `static/`: Directory containing static assets (CSS, JS) and user-uploaded images (`static/uploads/`).
