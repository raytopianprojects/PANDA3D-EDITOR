import os
import shutil
import sys
from subprocess import run

BUILD_DIR = "build"
SOURCE_DIRS = ["assets", "scripts", "shaders", "saves", "ui", "scenes"]
RUNTIME_SCRIPT = "Preview_build.py"

def clean_build():
    """Removes the old build directory if it exists."""
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR)

def copy_files():
    """Copies all necessary project files into the build directory."""
    for src_dir in SOURCE_DIRS:
        dest_dir = os.path.join(BUILD_DIR, src_dir)
        shutil.copytree(src_dir, dest_dir)

    # Copy runtime script (Preview_build.py) and rename it as game.py
    shutil.copy(RUNTIME_SCRIPT, os.path.join(BUILD_DIR, "game.py"))

def create_launcher():
    """Creates a launcher script for running the game."""
    launcher_content = """import os
from game import GamePreviewApp
app = GamePreviewApp()
app.run()
"""
    with open(os.path.join(BUILD_DIR, "run_game.py"), "w") as f:
        f.write(launcher_content)

def package_game():
    """Packages the game into an executable format."""
    os.chdir(BUILD_DIR)
    run(["pyinstaller", "--onefile", "--windowed", "run_game.py"])
    os.chdir("..")

if __name__ == "__main__":
    clean_build()
    copy_files()
    create_launcher()
    package_game()
    print("✅ Build completed! Check the 'build/' folder.")
