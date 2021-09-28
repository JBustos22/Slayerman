import json

def get_donations_data():
    global DONATION_DATA
    try:
        with open("dfwc/donations_data.json", 'r') as f:
            DONATION_DATA = json.loads(f.read())
    except FileNotFoundError:
        DONATION_DATA = {
            "current_row": 2,
            "total_amount": 0.
        }

def save_donations_data():
    global DONATION_DATA
    with open("dfwc/donations_data.json", 'w') as f:
        f.write(json.dumps(DONATION_DATA))


def main():
    import os.path
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    import json

    get_donations_data()
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '151R1CL_dvoW_M2eWTQWxH2UjJfWhsL3rhb-lC4B7oKI'
    global DONATION_DATA
    global SAMPLE_RANGE_NAME
    global TOTAL_AMOUNT
    SAMPLE_RANGE_NAME = f'A{DONATION_DATA["current_row"]}:F{DONATION_DATA["current_row"]}'
    creds = None
    if os.path.exists('dfwc/token.json'):
        creds = Credentials.from_authorized_user_file('dfwc/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'dfwc/credentials.json', SCOPES)
            creds = flow.run_local_server(port=27960)
        # Save the credentials for the next run
        with open('dfwc/token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    try:
        donation_line = result.get('values', [])[0]
    except:
        return

    if len(donation_line) == 6:
        date, country, tld, name, amount, comment = donation_line
        tld = tld.lower()
        amt_val = float(amount.strip('$'))
        updated_total = round(DONATION_DATA['total_amount'] + amt_val, 2)
        msg = f"**{amount}** donation by {f':flag_{tld}: **{name}**' if tld != 'xx' else name}"
        if comment != '.':
            msg += f': *"{comment}"*'
        msg += f'. The total prize pool is now **${updated_total}**!'

        DONATION_DATA['current_row'] += 1
        DONATION_DATA['total_amount'] = updated_total
        SAMPLE_RANGE_NAME = f"A{DONATION_DATA['current_row']}:F{DONATION_DATA['current_row']}"
        save_donations_data()
        return msg
    elif len(donation_line) == 4:
        action, arg_1, arg_2, done = donation_line

        if action == 'rollback':
            row_to_rb_to = int(arg_1)
            updated_total = round(float(arg_2.strip('$')), 2)
            DONATION_DATA['current_row'] = row_to_rb_to
            DONATION_DATA['total_amount'] = updated_total
            SAMPLE_RANGE_NAME = f"A{DONATION_DATA['current_row']}:F{DONATION_DATA['current_row']}"
            save_donations_data()
