# Daily Routine Tracker

A simple and effective project built with Django (Python) to help you create, manage, and reflect on your daily plans! This tool allows you to plan your day, track task completion, and receive a score based on your accomplishments—helping you build better habits and achieve meaningful self-reflection.

## Features

- **Daily Planning**: Easily set your daily goals and tasks.
- **Progress Tracking**: Mark tasks as complete throughout the day.
- **Auto-Scoring**: Get a score reflecting your daily accomplishments.
- **Self-Reflection**: Review your performance and identify areas for improvement.
- **User-Friendly Interface**: Simple and intuitive design for all users.

## Technology Stack

- **Backend:** [Django](https://www.djangoproject.com/) (Python)
- **Frontend:** Django Templates (customize as needed)
- **Database:** Default (SQLite) or configurable

## Getting Started

### Prerequisites

- [Python 3.7+](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/)
- [virtualenv](https://virtualenv.pypa.io/en/latest/) (recommended)

### Installation

```bash
git clone https://github.com/AdhAyush/Daily-Routine-Tracker.git
cd Daily-Routine-Tracker
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Project

```bash
python manage.py migrate
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/`.

## Usage

1. **Add Tasks**: Enter your tasks/goals for the day.
2. **Complete Tasks**: Check tasks as you complete them.
3. **View Score**: At the end of the day, see your score and reflect on your performance.
4. **Self-Reflect**: Use your daily score to motivate yourself and improve over time.

## Contributing

Contributions are welcome! Please open issues and submit pull requests for new features, bug fixes, or improvements.

1. Fork the repo.
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add your message'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a pull request.

## License

This project is open source, licensed under the [MIT License](LICENSE).

## Author

- [AdhAyush](https://github.com/AdhAyush)

---

> _"Track your day, build better habits, and reflect for a better tomorrow!"_
