import os

# Define folders to create
folders = [
    "app",
    "app/routes"
]

# Define files to create
files = [
    "app/__init__.py",
    "app/config.py",
    "app/database.py",
    "app/models.py",
    "app/routes/__init__.py",
    "app/routes/auth.py",
    "app/routes/user.py",
    ".env",
    "init_db.py",
    "run.py",
    "requirements.txt"
]

# Create directories
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"📁 Created folder: {folder}")

# Create empty files if they don't exist
for file in files:
    if not os.path.exists(file):
        with open(file, "w") as f:
            pass
        print(f"📄 Created file: {file}")

print("\n Folder structure created successfully!")