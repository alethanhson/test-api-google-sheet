import os.path

from fastapi import FastAPI
from pydantic import BaseModel
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = FastAPI()

creds = None
SPREADSHEET_ID = "1E1TqqJc7jc2ZMuXWxU8MWxqJCbR4Z9spGu5C7in7qvo"
RANGE_NAME = "Sheet1!A1:Z"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    'https://www.googleapis.com/auth/drive'
]

try:
    if os.path.exists("credentials.json"):
        creds = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)
except Exception as e:
    print(f"Failed to load credentials: {e}")

service = None
drive_service = None
if creds:
    try:
        service = build('sheets', 'v4', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Failed to build service: {e}")


class Sheet(BaseModel):
    spreadsheet_id: str
    sheet_name: str
    range_name: str


@app.get("/")
def get_sheet():
    result = None
    if service:
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()

        except Exception as e:
            print(f"Failed to get sheet: {e}")

    if result and result['values']:
        data = result.get('values', [])
        return {"result": data}
    else:
        return {"message": "Failed to get sheet."}


@app.get("/create-sheet")
def create_new_sheet():
    if service:
        try:
            spreadsheet_details = {
                'properties': {
                    'title': 'New Test Sheet'
                }
            }

            sheet = service.spreadsheets().create(body=spreadsheet_details,
                                                  fields='spreadsheetId').execute()
            sheetId = sheet.get('spreadsheetId')
            permission1 = {
                'type': 'user',
                'role': 'writer',
                'emailAddress': 'sonalt@flydinotech.com'
            }
            drive_service.permissions().create(fileId=sheetId, body=permission1).execute()

            return {"Sheet ID": sheetId}
        except Exception as e:
            print(f"Failed to create sheet: {e}")


@app.get("/update-sheet")
def update_sheet():
    if service:
        try:
            values = [['Ben', 'Stiller', 50, 'Male', 'New Jersey', 'USA',
                       '98989898989', 'j11292@example.com']]
            value_input_option = 'USER_ENTERED'
            body = {
                'values': values
            }
            rangeLast = getRangSheet()
            if not rangeLast:
                rangeLast = RANGE_NAME
            result = service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID, range=rangeLast,
                valueInputOption=value_input_option, body=body).execute()
            return {"result", result}
        except Exception as e:
            print(f"Failed to update sheet: {e}")


@app.get("/update-sheet-multiple")
def update_sheet_multiple():
    if service:
        try:
            values = [
                ['John', 'John', '20', 'Male', 'New Jersey', 'USA',
                    '98989898989', 'j11292@example.com'],
                ['Jane', 'Doe', '30', 'Female', 'California', 'USA',
                    '1234567890', 'jane.doe@example.com'],
                ['Bob', 'Smith', '25', 'Male', 'Texas', 'USA', '5555555555',
                    'bob.smith@example.com'],
            ]

            value_input_option = 'USER_ENTERED'
            body = {
                'values': values
            }

            rangeLast = getRangSheet()
            if not rangeLast:
                rangeLast = RANGE_NAME
            result = service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID, range=rangeLast,
                valueInputOption=value_input_option, body=body).execute()
            return {"result", result}
        except Exception as e:
            print(f"Failed to update sheet: {e}")


@app.get("/update-sheet-by-value/{value}")
def update_sheet_by_value(value: str):
    if service:
        try:
            filter_criteria = {
                'columnIndex': 0,
                'values': ['Value to Filter']
            }
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                'credentials.json', ['https://www.googleapis.com/auth/spreadsheets'])
            client = gspread.authorize(credentials)
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            sheet = spreadsheet.worksheet('Sheet1')
            list_of_lists = sheet.findall('j11292@example.com', in_column=8)
            
            matching_rows = []
            for cell in list_of_lists:
                row = cell.row
                value_b = sheet.cell(row, 6)
                print(value_b)
                if value_b == 'USAA':
                    matching_rows.append(row)

            return matching_rows
        except Exception as e:
            print(f"Failed to update sheet: {e}")


def getRangSheet():
    response = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    if response and 'values' in response:
        return "Sheet1!A" + str(len(response['values']) + 1) + ":Z"
    else:
        return False
