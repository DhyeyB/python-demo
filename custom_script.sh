#!/bin/bash

get_changed_files() {
    # Use git diff command to get the list of changed files
    output=$(git diff --name-only HEAD)
    # Filter out only the Python files
    python_files=$(echo "$output" | grep '\.py$')
    echo "$python_files"
}

run_pytype() {
    # Run pytype with the filtered Python files as arguments
    pytype "$@"
}

main() {
    # Get the list of changed Python files
    changed_files=$(get_changed_files)
    if [ -z "$changed_files" ]; then
        echo "No changed Python files detected."
        exit 0
    fi

    # Run pytype on the changed Python files
    run_pytype $changed_files
}

# Call main function when script is executed
main
