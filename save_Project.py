import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QFileDialog, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt


class UnityStartupWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Select a Project")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel("Select or Create a Project:")
        layout.addWidget(self.label)

        # List existing projects
        self.project_list = QListWidget()
        self.load_projects()
        layout.addWidget(self.project_list)

        # Select project button
        self.select_button = QPushButton("Open Project")
        self.select_button.clicked.connect(self.open_project)
        layout.addWidget(self.select_button)

        # Create new project section
        self.new_project_input = QLineEdit()
        self.new_project_input.setPlaceholderText("Enter new project name...")
        layout.addWidget(self.new_project_input)

        self.create_button = QPushButton("Create New Project")
        self.create_button.clicked.connect(self.create_project)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def load_projects(self):
        """Loads project folders from a predefined directory."""
        self.project_dir = "./projects"
        os.makedirs(self.project_dir, exist_ok=True)  # Ensure the directory exists
        self.project_list.clear()
        for project in os.listdir(self.project_dir):
            if os.path.isdir(os.path.join(self.project_dir, project)):
                self.project_list.addItem(project)

    def open_project(self):
        """Opens the selected project and launches the main app."""
        selected_item = self.project_list.currentItem()
        if selected_item:
            project_path = os.path.join(self.project_dir, selected_item.text())
            print(f"Opening project: {project_path}")
            self.launch_main_app(project_path)
        else:
            QMessageBox.warning(self, "No Project Selected", "Please select a project to open.")

    def create_project(self):
        """Creates a new project directory and updates the list."""
        project_name = self.new_project_input.text().strip()
        if not project_name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a valid project name.")
            return

        project_path = os.path.join(self.project_dir, project_name)
        if os.path.exists(project_path):
            QMessageBox.warning(self, "Project Exists", "A project with this name already exists.")
            return

        os.makedirs(project_path)
        self.load_projects()
        QMessageBox.information(self, "Project Created", f"Project '{project_name}' created successfully!")

    def launch_main_app(self, project_path):
        """Launches the main application with the selected project."""
        print(f"Launching main application with project: {project_path}")
        self.close()
        # Replace with your main application launch (e.g., `main.py`)
        os.system(f"python main.py {project_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UnityStartupWindow()
    window.show()
    sys.exit(app.exec_())
