# 🚀 Project Management System

A comprehensive corporate project management application built with Flask (Backend) and React/Vite (Frontend).

## 📋 Features

- **User Authentication** - Secure login (Admin-issued credentials)
- **Project Management** - Create, track, and manage projects
- **Task Management** - Assign and track tasks across teams
- **AI Assistant** - Integrated AI chatbot for productivity
- **Real-time Chat** - Group chats and DMs with file sharing
- **Analytics Dashboard** - Real-time insights and reports
- **Role-Based Access** - Admin, Team Leader, and Employee roles
- **Modern UI** - Built with Tailwind CSS and Lucide Icons

## 🛠️ Tech Stack

### Backend
- **Language**: Python 3.9+
- **Framework**: Flask
- **Database**: SQLite / SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **API Style**: RESTful

### Frontend
- **Framework**: React.js
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router DOM 6
- **Icons**: Lucide React
- **HTTP Client**: Axios

## 📁 Project Structure

```
project-management-app/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── utils/           # Helper functions
│   │   └── __init__.py      # App factory
│   ├── config.py            # Configuration
│   ├── run.py               # Application entry point
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── contexts/        # React Context (Auth, etc.)
│   │   ├── pages/           # Application pages
│   │   └── App.jsx          # Main component
│   ├── package.json         # JS dependencies
│   └── vite.config.js       # Vite configuration
│
└── README.md
```

## 🚀 Getting Started

### Backend Setup

1.  **Navigate to backend directory**
    ```bash
    cd backend
    ```

2.  **Create and activate virtual environment**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application**
    ```bash
    python run.py
    ```
    The backend API will run at `http://localhost:5000`.

### Frontend Setup

1.  **Navigate to frontend directory**
    ```bash
    cd frontend
    ```

2.  **Install dependencies**
    ```bash
    npm install
    ```

3.  **Run the development server**
    ```bash
    npm run dev
    ```
    The frontend will run at `http://localhost:5173` (or the port shown in terminal).

## 📝 Usage

1.  Start the backend server first.
2.  Start the frontend development server.
3.  Navigate to the frontend URL in your browser.
4.  Login or register to start managing projects.

## 🤝 Contributing

This is a portfolio project. Feel free to fork and customize!

## 📄 License

MIT License

## 👤 Author

**Pattipu Shyam**
- GitHub: [@Shyam2119](https://github.com/Shyam2119)