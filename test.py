acc=''
import requests
import base64
import json

# Configuration




# ── Option 1: Fetch tasks via WIQL query ──────────────────────────────────────
def fetch_tasks_wiql():
    url = f"{BASE_URL}/wit/wiql?api-version=7.1"
    query = {
        "query": """
            SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo]
            FROM WorkItems
            WHERE [System.WorkItemType] = 'Task'
            ORDER BY [System.ChangedDate] DESC
        """
    }
    response = requests.post(url, headers=headers, json=query)
    response.raise_for_status()
    
    work_item_refs = response.json().get("workItems", [])
    print(f"Found {len(work_item_refs)} tasks")
    return work_item_refs

# ── Option 2: Fetch full details for a list of work item IDs ─────────────────
def fetch_work_item_details(ids: list[int]):
    if not ids:
        return []
    
    ids_str = ",".join(str(i) for i in ids)
    url = f"{BASE_URL}/wit/workitems?ids={ids_str}&fields=System.Id,System.Title,System.State,System.AssignedTo,System.Description&api-version=7.1"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("value", [])

# ── Option 3: Fetch tasks from a specific iteration/sprint ───────────────────
def fetch_tasks_by_sprint(team: str, iteration_path: str):
    url = f"{BASE_URL}/wit/wiql?api-version=7.1"
    query = {
        "query": f"""
            SELECT [System.Id], [System.Title], [System.State]
            FROM WorkItems
            WHERE [System.WorkItemType] = 'Task'
            AND [System.IterationPath] = '{iteration_path}'
        """
    }
    response = requests.post(url, headers=headers, json=query)
    response.raise_for_status()
    return response.json().get("workItems", [])

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Step 1: Get task IDs
    task_refs = fetch_tasks_wiql()
    
    # Step 2: Get full details (API accepts max 200 IDs at once)
    ids = [item["id"] for item in task_refs[:200]]
    tasks = fetch_work_item_details(ids)
    
    # Step 3: Print results
    for task in tasks:
        fields = task["fields"]
        print(f"[{task['id']}] {fields['System.Title']} — {fields['System.State']}")
    
    # Optional: Save to JSON
    with open("tasks.json", "w") as f:
        json.dump(tasks, f, indent=2)
    print("\nSaved to tasks.json")