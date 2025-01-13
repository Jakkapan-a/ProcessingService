from app.models.filemanager import FileManager
def get_file_list(search = None, page = 1, per_page = 10):
    """
    Get file manager entries with search and pagination

    Args:
        search (str, optional): Search term for filtering files
        page (int): Current page number (default: 1)
        per_page (int): Number of items per page (default: 10)

    Returns:
        dict: Dictionary containing:
            - items: List of FileManager objects
            - total: Total number of items
            - pages: Total number of pages
            - current_page: Current page number
            - per_page: Items per page
    """


    query = FileManager.query

    if search:
        query = query.filter(FileManager.name.ilike(f'%{search}%'))

    # Get the items for the current page
    total_items = query.count()

    # Calculate the number of pages
    total_pages = (total_items + per_page - 1) // per_page # integer division

    # Ensure the page number is within the valid range
    page = min(max(page, 1), total_pages) if total_pages > 0 else 1

    # Get the items for the current page
    items = query.order_by(FileManager.id).limit(per_page).offset((page - 1) * per_page).all()



    return {
        'items': [item.to_dict() for item in items],
        'pagination': {
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }


def validate_name(name):
    """
    Validate the name of file manager entry

    Args:
        name (str): Name of the file

    Returns:
        bool: True if the name is valid, False otherwise
    """
    if not name:
        return False

    if len(name) > 255:
        return False

    query = FileManager.query.filter(FileManager.name == name).first()
    return query is None # True if query is None, False otherwise