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

# Organizing the data
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

# Create folders using the Vantage API
base_url = "https://api.vantage.sh/v2/folders"

for business_unit, cost_centers in data_structure.items():
    try:
        bu_data = {
            "title": business_unit,
        }
        print(f"Attempting to create Business Unit Folder: {business_unit}")
        bu_response = requests.post(base_url, headers=headers, json=bu_data)
        bu_response.raise_for_status()
        bu_token = json.loads(bu_response.text).get('token')
        print(f"Successfully created Business Unit Folder: {business_unit}, Token: {bu_token}")

        for cost_center, account_ids in cost_centers.items():
            try:
                cc_data = {
                    "title": cost_center,
                    "parent_folder_token": bu_token,
                }
                print(f"Attempting to create Cost Center Folder: {cost_center} in {business_unit}")
                cc_response = requests.post(base_url, headers=headers, json=cc_data)
                cc_response.raise_for_status()
                cc_token = json.loads(cc_response.text).get('token')
                print(f"Successfully created Cost Center Folder: {cost_center} in {business_unit}, Token: {cc_token}")

                for account_id in account_ids:
                    try:
                        acc_data = {
                            "title": account_id,
                            "parent_folder_token": cc_token,
                        }
                        print(f"Attempting to add Account ID: {account_id} to {cost_center} in {business_unit}")
                        acc_response = requests.post(base_url, headers=headers, json=acc_data)
                        acc_response.raise_for_status()
                        print(f"Successfully added Account ID: {account_id} to {cost_center} in {business_unit}")

                    except requests.exceptions.HTTPError as e:
                        print(f"Error adding Account ID {account_id} to {cost_center} in {business_unit}: {e}")

            except requests.exceptions.HTTPError as e:
                print(f"Error creating folder for cost center {cost_center} in {business_unit}: {e}")

    except requests.exceptions.HTTPError as e:
        print(f"Error creating business unit {business_unit}: {e}")

print("Script execution completed.")
