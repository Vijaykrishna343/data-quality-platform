sessions = {}


def create_session(dataset_id, original_path):
    sessions[dataset_id] = {
        "original_path": original_path,
        "cleaned_path": None,
    }


def get_session(dataset_id):
    return sessions.get(dataset_id)


def set_cleaned_path(dataset_id, cleaned_path):
    if dataset_id in sessions:
        sessions[dataset_id]["cleaned_path"] = cleaned_path