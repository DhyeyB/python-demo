import subprocess
import sys
from setuptools import setup

def get_changed_files():
    try:
        # Use git diff command to get the list of changed files
        output = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'])
        changed_files = output.decode('utf-8').split('\n')
        # Filter out only the Python files
        python_files = [file for file in changed_files if file.endswith('.py')]
        return python_files
    except subprocess.CalledProcessError:
        print("Error: Failed to get changed files. Make sure your project is a Git repository.")
        sys.exit(1)

def run_pytype(files):
    try:
        # Run pytype with the filtered Python files as arguments
        subprocess.run(['pytype'] + files, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Pytype failed with exit code {e.returncode}")
        sys.exit(1)

def main():
    # Get the list of changed Python files
    changed_files = get_changed_files()
    if not changed_files:
        print("No changed Python files detected.")
        sys.exit(0)

    # Run pytype on the changed Python files
    run_pytype(changed_files)

if __name__ == "__main__":
    # Call main function when script is executed
    main()

# Setup configuration
setup(
    name='pre_commit_pytype',
    version='2023.5.8',
    install_requires=['pytype==2023.5.8'],
)

