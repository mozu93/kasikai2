
import os
import subprocess
import sys

def main():
    print("Setting up the Conference Room Booking System...")

    # Create necessary directories
    print("Creating directories...")
    try:
        os.makedirs("申し込みデータ", exist_ok=True)
        os.makedirs("処理済み", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        print("  - 申し込みデータ")
        print("  - 処理済み")
        print("  - data")
        print("Directories created successfully.")
    except Exception as e:
        print(f"Error creating directories: {e}")
        sys.exit(1)

    # Install dependencies
    print("\nInstalling required packages from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Packages installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        print("Please make sure pip is installed and you have an internet connection.")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: requirements.txt not found.")
        sys.exit(1)

    print("\nSetup complete!")
    print("You can now run the application using:")
    print("  - run_host_services.bat: To run the application in the background.")
    print("  - start_server.bat: To run the web server for local viewing.")

if __name__ == "__main__":
    main()
