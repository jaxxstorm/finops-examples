import argparse
import requests
import csv
import json

# Setting up argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--token", help="Vantage access token")
parser.add_argument("--csv", help="Path to CSV file to read")
args = parser.parse_args()

# API URL and headers
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + args.token,
}

# Function to retrieve all folders and return as a dictionary
# The dictionary will have a tuple (title, parent_folder_token) as key and token as value
def get_all_folders():
    try:
        print("Retrieving existing folders...")
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        folders_data = response.json()['folders']
        return {(folder['title'], folder['parent_folder_token']): folder['token'] for folder in folders_data}
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving folders: {e}")
        return {}

# Retrieve all existing folders
base_url = "https://api.vantage.sh/v2/folders"
existing_folders = get_all_folders()

# Organizing the data from CSV
data_structure = {}
with open(args.csv, mode='r', newline='', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)  # Skip the header
    for row in csv_reader:
        business_unit, cost_center, account_id = row
        if business_unit not in data_structure:
            data_structure[business_unit] = {}
        if cost_center not in data_structure[business_unit]:
            data_structure[business_unit][cost_center] = []
        data_structure[business_unit][cost_center].append(account_id)
        print(f"Processed row: Business Unit = {business_unit}, Cost Center = {cost_center}, Account ID = {account_id}")

print("Finished processing CSV data. Starting API requests...")

# Process data and create folders if they don't exist
for business_unit, cost_centers in data_structure.items():
    print(f"Checking/Creating folder for Business Unit: {business_unit}")
    bu_token = existing_folders.get((business_unit, None))
    if not bu_token:
        try:
            bu_data = {"title": business_unit}
            print(f"Creating Business Unit Folder: {business_unit}")
            bu_response = requests.post(base_url, headers=headers, json=bu_data)
            bu_response.raise_for_status()
            bu_token = json.loads(bu_response.text).get('token')
            existing_folders[(business_unit, None)] = bu_token
            print(f"Created Business Unit Folder: {business_unit}, Token: {bu_token}")
        except requests.exceptions.HTTPError as e:
            print(f"Error creating business unit {business_unit}: {e}")

    for cost_center, account_ids in cost_centers.items():
        print(f"Checking/Creating folder for Cost Center: {cost_center} in {business_unit}")
        cc_token = existing_folders.get((cost_center, bu_token))
        if not cc_token:
            try:
                cc_data = {
                    "title": cost_center,
                    "parent_folder_token": bu_token,
                }
                print(f"Creating Cost Center Folder: {cost_center} in {business_unit}")
                cc_response = requests.post(base_url, headers=headers, json=cc_data)
                cc_response.raise_for_status()
                cc_token = json.loads(cc_response.text).get('token')
                existing_folders[(cost_center, bu_token)] = cc_token
                print(f"Created Cost Center Folder: {cost_center} in {business_unit}, Token: {cc_token}")
            except requests.exceptions.HTTPError as e:
                print(f"Error creating folder for cost center {cost_center} in {business_unit}: {e}")

        for account_id in account_ids:
            print(f"Checking/Adding Account ID: {account_id} to Cost Center: {cost_center} in {business_unit}")
            acc_token = existing_folders.get((account_id, cc_token))
            if not acc_token:
                try:
                    acc_data = {
                        "title": account_id,
                        "parent_folder_token": cc_token,
                    }
                    print(f"Adding Account ID: {account_id} to Cost Center: {cost_center} in {business_unit}")
                    acc_response = requests.post(base_url, headers=headers, json=acc_data)
                    acc_response.raise_for_status()
                    existing_folders[(account_id, cc_token)] = json.loads(acc_response.text).get('token')
                    print(f"Added Account ID: {account_id} to Cost Center: {cost_center} in {business_unit}")
                except requests.exceptions.HTTPError as e:
                    print(f"Error adding Account ID {account_id} to {cost_center} in {business_unit}: {e}")

print("Script execution completed.")
