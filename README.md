# Menu Summarizer

A small Flask web application.

## Project Structure

```
menu-summarizer/
├── app.py                 # Main Flask application file
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── templates/            # HTML templates
│   ├── index.html       # Homepage template
│   ├── 404.html         # 404 error page
│   └── 500.html         # 500 error page
└── static/               # Static files
    ├── css/
    │   └── style.css    # Main stylesheet
    └── js/
        └── main.js      # Main JavaScript file
```

## Setup Instructions

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Visit the app:**
   Open your browser to `http://localhost:5000`

## Development

- The app runs in debug mode by default (set `DEBUG=False` in `.env` for production)
- Templates are in the `templates/` directory
- Static files (CSS, JS, images) go in the `static/` directory
- Add new routes in `app.py`

## Adding Dependencies

When you add new Python packages:
```bash
pip install package-name
pip freeze > requirements.txt
```
