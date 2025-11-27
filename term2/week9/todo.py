from typing import Dict, List, Any
import csv
import os

from fastapi import FastAPI, APIRouter, HTTPException


DATA_FILE = 'todo_data.csv'

# In-memory list of todo dicts
todo_list: List[Dict[str, Any]] = []


def _ensure_data_file_exists() -> None:
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='') as f:
            pass


def _load_todos_from_csv() -> List[Dict[str, Any]]:
    _ensure_data_file_exists()
    with open(DATA_FILE, 'r', newline='') as f:
        try:
            # Peek first line to decide if header exists
            first_pos = f.tell()
            first_line = f.readline()
            f.seek(first_pos)
            if not first_line:
                return []
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return []
            items: List[Dict[str, Any]] = []
            for row in reader:
                # Convert empty strings back to None to keep semantics simple
                normalized: Dict[str, Any] = {}
                for k, v in row.items():
                    normalized[k] = v if v != '' else None
                items.append(normalized)
            return items
        except csv.Error:
            return []


def _save_todos_to_csv(items: List[Dict[str, Any]]) -> None:
    _ensure_data_file_exists()
    if not items:
        # If empty, truncate file
        open(DATA_FILE, 'w').close()
        return
    # Compute union of all keys to form header
    fieldnames: List[str] = []
    seen: set = set()
    for entry in items:
        for key in entry.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in items:
            row: Dict[str, Any] = {k: entry.get(k, '') for k in fieldnames}
            writer.writerow(row)


# Initialize memory from CSV at import time to avoid startup warnings
todo_list = _load_todos_from_csv()


router = APIRouter(prefix='/todo')


@router.post('/', name='add_todo')
def add_todo(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail='Input must be a dict.')
    if not payload:
        # Bonus: warn when empty dict provided
        raise HTTPException(status_code=400, detail='Empty dict is not allowed.')
    todo_list.append(payload)
    _save_todos_to_csv(todo_list)
    return {'ok': True, 'added': payload}


@router.get('/', name='retrieve_todo')
def retrieve_todo() -> Dict[str, Any]:
    # Ensure we reflect any external file updates
    global todo_list
    todo_list = _load_todos_from_csv()
    return {'todo_list': todo_list}


app = FastAPI()
app.include_router(router)


