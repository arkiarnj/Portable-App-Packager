import os
import shutil
import subprocess
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def clear_screen():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        pass  # اگر اجرا نشد، بی‌خیال شو

def is_tool_installed(tool_name):
    try:
        subprocess.run([tool_name, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def copy_supporting_files(src_folder, dest_folder, exclude_files=None):
    if exclude_files is None:
        exclude_files = []

    if not os.path.exists(src_folder):
        logging.error(f"Source folder '{src_folder}' does not exist.")
        return False

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    for item in os.listdir(src_folder):
        if item in exclude_files:
            continue
        s = os.path.join(src_folder, item)
        d = os.path.join(dest_folder, item)
        try:
            if os.path.isdir(s):
                # پشتیبانی از پایتون قبل از 3.8 بدون dirs_exist_ok
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        except Exception as e:
            logging.warning(f"Failed to copy {s} to {d}: {e}")
    return True

def package_python_project(project_path, output_dir, onefile=True, icon_path=None):
    if not os.path.isfile(project_path):
        logging.error(f"Project file '{project_path}' does not exist.")
        return False

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    command = [
        "pyinstaller",
        project_path,
        "--distpath",
        output_dir,
        "--noconfirm",
        "--clean"
    ]

    if onefile:
        command.append("-F")

    if icon_path:
        if os.path.isfile(icon_path):
            command.extend(["--icon", icon_path])
        else:
            logging.warning(f"Icon file '{icon_path}' not found. Ignoring icon.")

    logging.info(f"Packaging Python project '{project_path}' into '{output_dir}' (onefile={onefile})...")

    try:
        subprocess.run(command, check=True)
        logging.info("✅ Packaging completed.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Error during packaging: {e}")
        return False

def package_csharp_flow():
    if not is_tool_installed("dotnet"):
        logging.error("❌ dotnet SDK not found in PATH. Please install it from https://dotnet.microsoft.com/download")
        return

    project_path = input("Enter full path to your C# project file (*.csproj): ").strip()
    if not (os.path.isfile(project_path) and project_path.lower().endswith(".csproj")):
        logging.error("Invalid .csproj file path.")
        return

    output_dir = input("Enter output directory: ").strip()
    if output_dir == "":
        logging.error("Output directory cannot be empty.")
        return
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            logging.error(f"Cannot create output directory: {e}")
            return

    command = [
        "dotnet",
        "publish",
        project_path,
        "-c",
        "Release",
        "-r",
        "win-x64",
        "--self-contained",
        "true",
        "/p:PublishSingleFile=true",
        "-o",
        output_dir
    ]

    logging.info(f"Packaging C# project '{project_path}' to '{output_dir}' ...")
    try:
        subprocess.run(command, check=True)
        logging.info("✅ C# packaging done.")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Error during C# packaging: {e}")

def package_java_flow():
    if not is_tool_installed("jpackage"):
        logging.error("❌ jpackage tool not found. Please install JDK 14 or higher from https://adoptium.net/")
        return

    jar_path = input("Enter full path to your Java .jar file: ").strip()
    if not (os.path.isfile(jar_path) and jar_path.lower().endswith(".jar")):
        logging.error("Invalid JAR file path.")
        return

    output_dir = input("Enter output directory: ").strip()
    if output_dir == "":
        logging.error("Output directory cannot be empty.")
        return
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            logging.error(f"Cannot create output directory: {e}")
            return

    app_name = input("Enter application name: ").strip()
    if app_name == "":
        logging.error("Application name cannot be empty.")
        return

    command = [
        "jpackage",
        "--input",
        os.path.dirname(jar_path),
        "--name",
        app_name,
        "--main-jar",
        os.path.basename(jar_path),
        "--type",
        "exe",
        "--dest",
        output_dir
    ]

    logging.info(f"Packaging Java app '{app_name}' with jpackage to '{output_dir}' ...")
    try:
        subprocess.run(command, check=True)
        logging.info("✅ Java packaging done.")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Error during Java packaging: {e}")

def copy_files_flow():
    src = input("Enter source file or folder path: ").strip()
    if not os.path.exists(src):
        logging.error("Source path does not exist.")
        return

    dest = input("Enter destination directory: ").strip()
    if dest == "":
        logging.error("Destination directory cannot be empty.")
        return

    if not os.path.exists(dest):
        create_dir = input("Destination does not exist. Create it? (y/n): ").strip().lower()
        if create_dir == 'y':
            try:
                os.makedirs(dest)
            except Exception as e:
                logging.error(f"Cannot create destination directory: {e}")
                return
        else:
            logging.info("Destination directory not created. Operation cancelled.")
            return

    try:
        if os.path.isfile(src):
            shutil.copy2(src, dest)
            logging.info(f"✅ File copied to {dest}")
        else:
            dest_path = os.path.join(dest, os.path.basename(src))
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src, dest_path)
            logging.info(f"✅ Folder copied to {dest_path}")
    except Exception as e:
        logging.error(f"❌ Error copying: {e}")

def show_about():
    clear_screen()
    print("""
Portable App Packager v1.1
Author: Arkiarnj

This tool helps you package projects from
different programming languages into
portable executables or folders.

Supports Python, C#, Java, and generic files.

Make sure required tools are installed:
- Python & PyInstaller for Python projects
- .NET SDK for C# projects
- JDK 14+ for Java projects (with jpackage tool)

Thank you for using this tool!
""")
    input("\nPress Enter to return to menu...")

def main_menu():
    clear_screen()
    print("""
Portable App Packager
---------------------

1) Package Python project
2) Package C# project (dotnet publish)
3) Package Java project (jpackage)
4) Copy arbitrary files/folders
5) About
6) Exit
""")

def package_python_flow():
    project_path = input("Enter path to your main Python file (e.g. main.py): ").strip()
    if not (os.path.isfile(project_path) and project_path.lower().endswith(".py")):
        logging.error("Invalid Python file path. Returning to main menu.")
        input("Press Enter to continue...")
        return

    project_folder = os.path.dirname(project_path)
    output_dir = input("Enter output directory: ").strip()
    if output_dir == "":
        logging.error("Output directory cannot be empty. Returning to main menu.")
        input("Press Enter to continue...")
        return

    onefile_input = input("Create single EXE file? (y/n): ").strip().lower()
    onefile = onefile_input == 'y'

    icon_path = input("Enter icon file path (leave empty for none): ").strip()
    if icon_path == "":
        icon_path = None

    success = package_python_project(project_path, output_dir, onefile, icon_path)
    if success and not onefile:
        logging.info("Copying supporting files...")
        copy_supporting_files(project_folder, output_dir, exclude_files=[os.path.basename(project_path)])
    input("Press Enter to continue...")

def main():
    while True:
        main_menu()
        choice = input("Select an option: ").strip()
        if choice == "1":
            package_python_flow()
        elif choice == "2":
            package_csharp_flow()
            input("Press Enter to continue...")
        elif choice == "3":
            package_java_flow()
            input("Press Enter to continue...")
        elif choice == "4":
            copy_files_flow()
            input("Press Enter to continue...")
        elif choice == "5":
            show_about()
        elif choice == "6":
            logging.info("Exiting...")
            break
        else:
            logging.warning("Invalid choice, please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
