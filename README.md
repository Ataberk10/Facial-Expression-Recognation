# Facial Expression Recognation Using Computer Vision

## Introduction

This project is a web application built with Python and Django that allows users to analyze facial expressions in uploaded photos. Users can register, log in, upload images containing faces, add metadata, and the application will use a machine learning model (transformers) to predict the dominant facial expression. Users can then view, manage, and delete their analysis history through a personal dashboard.

This application serves as a practical example of integrating a Computer Vision model into a web framework, handling user authentication, file uploads, and database interactions.

## Features

Based on the project requirements:

*   **FR001: User Authentication:** Secure user registration (Email, Username, Password) and login system using Django's built-in authentication.
*   **FR009: User Logout:** Secure session termination.
*   **FR002: New Query Creation:** Logged-in users can initiate a new analysis query from their dashboard.
*   **FR003: Face Photo Upload:** Users can upload common image formats (JPEG, PNG) containing faces. Includes basic client/server-side validation hints (though full implementation might vary).
*   **FR004: Metadata Entry:** Users must provide a subject name and can add optional notes for each query.
*   **FR005: Automated Expression Analysis:** Upon submission, the backend triggers an ONNX-based model to analyze the uploaded photo and detect the facial expression (e.g., Happy, Sad, Surprised) and confidence score.
*   **FR006: Query History:** Dashboard displays a paginated list of the user's past queries (thumbnail, name, date, result).
*   **FR007: Query Details:** Users can view a detailed page for each query showing the full-size photo, metadata, timestamp, detected expression, and confidence score.
*   **FR008: Query Deletion:** Users can delete past queries (with confirmation) from the list or detail view. Associated image files are also removed.
*   **FR010: Responsive UI:** The user interface is designed using Bootstrap 5 to be responsive and usable on both desktop and mobile devices.
*   **FR011: Secure Data Handling:** Implements basic security practices like CSRF protection, hashed passwords, HTTPS (requires deployment configuration), and stores user-uploaded images in user-specific directories within a protected media root.

## Technology Stack

*   **Backend:** Python 3.x, Django 5.x
*   **Database:** SQLite (Default for development), easily configurable for PostgreSQL, MySQL, etc.
*   **ML Inference:** transformers
*   **Image Handling:** Pillow - primarily for image reading
*   **Frontend:** HTML5, CSS3, Bootstrap 5 (via CDN)
*   **Environment Management:** `venv`

## Setup and Installation

Follow these steps to set up the project locally:

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory-name>
    ```

2.  **Create and Activate Virtual Environment:**
    It's highly recommended to use a virtual environment.
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    Install all required packages listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
    *The key packages installed through the steps above were `django`, `pillow`, `transformers`.*

4.  **Place Your Model:**
    *   This application requires you to provide your own pre-trained facial expression classification model in ONNX format.
    *   Create a directory named `ml_models` in the project root (at the same level as `manage.py`).
    *   Place your `.safetensors` model file inside this directory.
    *   Place your `config.json` model file inside this directory.
    *   Place your `preprocessor_config.json` model file inside this directory.

5.  **Apply Database Migrations:**
    This creates the necessary database tables based on the models defined in `queries/models.py`.
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Create a Superuser (Admin Account):**
    This allows you to access the Django admin interface (`/admin/`).
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set a username, email (optional), and password.

## Running the Application

1.  **Start the Development Server:**
    ```bash
    python manage.py runserver
    ```

2.  **Access the Application:**
    Open your web browser and navigate to `http://127.0.0.1:8000/`.

**Note on Development Server:**
*   The development server (`runserver`) is **not suitable for production**.
*   It runs with `DEBUG=True` by default (in `core/settings.py`), which exposes potentially sensitive information. Set `DEBUG=False` in production.
*   The way media files (`MEDIA_ROOT`) are served in `core/urls.py` (`static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`) is also only for development. In production, your web server (e.g., Nginx, Apache) should be configured to serve these files directly.

## Usage Workflow

1.  **Visit the Site:** Go to the application's home page.
2.  **Sign Up:** Click "Sign Up", fill in the registration form (username, email, password), and submit. You will be automatically logged in.
3.  **Log In:** If you already have an account, click "Login" and enter your credentials.
4.  **Navigate Dashboard:** After logging in, you'll be on the home page or redirected to your query list ("My Queries").
5.  **Create New Query:** Click "New Query".
6.  **Upload & Submit:** Fill in the "Subject Name", upload a face photo using the file input, add optional "Notes", and click "Analyze Expression".
7.  **View Results:** You will be redirected to the Query Detail page, showing the uploaded photo, metadata, and the detected expression/confidence score from the model analysis.
8.  **Review History:** Navigate to "My Queries" to see a list of all your past analyses.
9.  **Delete Query:** From the "My Queries" list or the Query Detail page, click the "Delete" button and confirm the action to remove a query and its associated image.
10. **Log Out:** Click your username in the navbar and select "Logout".

## Folder Structure Overview
```
.
├── .venv/ # Virtual environment directory
├── core/ # Django project configuration
│ ├── init.py
│ ├── settings.py # Project settings
│ ├── urls.py # Project-level URL routing
│ ├── wsgi.py
│ └── asgi.py
├── media/ # Root directory for user-uploaded files (created automatically)
│ └── user_<id>/ # User-specific subdirectories
│ └── ... # Uploaded images
├── ml_models/ # Directory for ONNX model(s)
│ └── config.json
│ └── preprocessor_config.json
│ └── model.safetensors # <--- PLACE YOUR MODEL HERE
├── queries/ # Django app for handling queries
│ ├── init.py
│ ├── admin.py # Admin interface configuration
│ ├── analysis.py # <--- MODEL INFERENCE LOGIC (NEEDS CUSTOMIZATION)
│ ├── apps.py
│ ├── forms.py # Django forms (Signup, Query Creation)
│ ├── migrations/ # Database migration files
│ ├── models.py # Database models (FacialExpressionQuery)
│ ├── tests.py
│ └── views.py # Application views/logic
│ └── urls.py # App-level URL routing
├── templates/ # HTML templates
│ ├── base.html # Base template with Bootstrap
│ ├── home.html
│ ├── registration/ # Auth-related templates
│ │ ├── login.html
│ │ └── signup.html
│ └── queries/ # Query-related templates
│ ├── query_confirm_delete.html
│ ├── query_detail.html
│ ├── query_form.html
│ └── query_list.html
├── manage.py # Django's command-line utility
├── db.sqlite3 # Development database file
├── pyproject.toml
├── README.md # This file
├── uv.lock
└── requirements.txt # Python package dependencies
```


## Future Enhancements / TODO

*   **Asynchronous Analysis:** Implement background tasks (e.g., using Celery & Redis/RabbitMQ) for model inference to avoid blocking web requests and handle longer processing times.
*   **Improved Error Handling:** Provide more specific feedback for analysis failures (e.g., "No face detected", "Image too small").
*   **Advanced UI:** Implement features like image cropping/preview before upload, displaying bounding boxes for detected faces.
*   **Testing:** Add comprehensive unit and integration tests.
*   **Deployment:** Document steps for deploying to a production environment (e.g., using Docker, Nginx, Gunicorn).
*   **Model Management:** Allow uploading/selecting different analysis models via the UI.
*   **Scalability:** Optimize database queries and potentially switch to a more robust database for higher loads.

## License

This project is licensed under the MIT License
