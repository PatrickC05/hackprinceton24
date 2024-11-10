# Django Project

## Setup Instructions

Follow these steps to set up and run the Django project.

### Prerequisites

- Python 3.x
- pip (Python package installer)
- virtualenv (optional but recommended)

### Installation

1. **Clone the repository:**

2. **Create and activate a virtual environment (optional but recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

### Database Setup

4. **Apply migrations to set up the database:**

    ```bash
    python manage.py migrate
    ```

### Running the Server

5. **Start the development server:**

    ```bash
    python manage.py runserver
    ```

6. **Open your web browser and visit:**

    ```
    http://127.0.0.1:8000/
    ```