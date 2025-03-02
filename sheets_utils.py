# sheets_utils.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheets_client(service_account_path='credentials/service_account_credentials.json'):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_path, scope)
    client = gspread.authorize(creds)
    return client

def get_all_companies(sheet_name):
    """
    Returns a list of company names from the 'Company' column.
    Assumes the header row includes a column named 'Company'.
    """
    client = get_sheets_client()
    sheet = client.open(sheet_name).sheet1
    records = sheet.get_all_records()
    companies = [str(record['Company']).strip() for record in records if record.get('Company')]
    return companies

def update_application_status(sheet_name, company_name, status, date_applied=None):
    """
    Updates the row for the given company with the new status.
    Returns True if an existing row was updated; otherwise, False.
    """
    client = get_sheets_client()
    sheet = client.open(sheet_name).sheet1
    records = sheet.get_all_records()
    found_row = None
    for idx, record in enumerate(records, start=2):  # row 1 is header
        if str(record['Company']).strip().lower() == company_name.lower():
            found_row = idx
            break
    if found_row is not None:
        sheet.update_cell(found_row, 5, status)  # assuming "Status" is column E (5)
        if date_applied:
            sheet.update_cell(found_row, 6, date_applied)  # assuming "Applied Date" is column F (6)
        return True
    else:
        return False

def append_new_row(sheet_name, job_title, company_name, status, date_applied=None, notes=""):
    """
    Appends a new row to the sheet.
    Column layout example:
      A: Job Title, B: Company, C: Source, D: Found, E: Status, F: Applied Date, G: Notes
    """
    client = get_sheets_client()
    sheet = client.open(sheet_name).sheet1
    row_data = [
        job_title or "",
        company_name or "",
        "",  # Source (optional)
        "",  # Found (optional)
        status or "",
        date_applied or "",
        notes
    ]
    sheet.append_row(row_data, value_input_option="USER_ENTERED")
