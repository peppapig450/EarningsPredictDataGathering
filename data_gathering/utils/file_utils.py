from pathlib import Path


def get_project_root_directory(
    marker_file="pyproject.toml", return_data_gathering=True
):
    """
    Finds the project root directory by looking for a marker file.

    Parameters:
        marker_file (str): The file that marks the project root directory.
        return_data_gathering (bool): Whether to return the data_gathering directory if found.

    Returns:
        Path: The project root directory if return_data_gathering is False,
              or the data_gathering directory if found and return_data_gathering is True.
              Returns None if neither is found.
    """
    current_path = Path(__file__).resolve()

    for parent in current_path.parents:
        if (parent / marker_file).exists():
            project_root = parent
            if return_data_gathering:
                data_gathering_dir = project_root / "data_gathering"
                if data_gathering_dir.exists():
                    return data_gathering_dir
                raise FileNotFoundError(
                    f"The data_gathering directory does not exist under {project_root}."
                )
            return project_root

    # If no marker file is found and return_data_gathering is False, raise FileNotFoundException
    if not return_data_gathering:
        raise FileNotFoundError(
            f"No marker file '{marker_file}' found to determine project root."
        )

    return None


def create_path(*args, **kwargs):
    """
    Creates a dynamic path using the provided path components and optional starting path.

    Parameters:
        *args: Arbitrary number of path components.
        **kwargs: Optional keyword arguments.
            - starting_path (str or Path, optional): The base directory to start from.
                                                     Defaults to the current directory if None.
            - check_exists (bool, optional): If True, checks whether the constructed path exists.
                                             Defaults to True.

    Returns:
        Path object representing the constructed path.

    Raises:
        FileNotFoundError: If check_exists is True and the constructed path does not exist.
    """
    starting_path = kwargs.get("starting_path", Path.cwd())
    check_exists = kwargs.get("check_exists", True)

    if not isinstance(starting_path, Path):
        starting_path = Path(starting_path)

    constructed_path = starting_path.joinpath(*args)

    if check_exists and not constructed_path.exists():
        raise FileNotFoundError(f"The path {constructed_path} does not exist.")

    return constructed_path


# TODO: absolute could be used here i think
def get_file_path_in_project(*path_components, marker_file="pyproject.toml") -> Path:
    """
    Retrieves a file path relative to the project root directory.

    Parameters:
        *path_components: Arbitrary number of path components.
        marker_file (str): The file that marks the project root directory.

    Returns:
        Path: The constructed file path.

    Raises:
        FileNotFoundError: If the project root directory cannot be determined.
    """
    try:
        project_root = get_project_root_directory(marker_file=marker_file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Failed to determine project root: {e}") from e

    file_path = project_root / Path(*path_components)

    return file_path
