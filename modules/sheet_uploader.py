import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def upload_to_google_sheet(trade_logs, summary_rows):
    # Step 1: Auth
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Step 2: Open the sheet
    sheet_url = "https://docs.google.com/spreadsheets/d/10mhP8DCnc2czx85DhJ8W1sL2Am36jkLSdRl5CojVJC4/edit"
    sheet = client.open_by_url(sheet_url)

    # Step 3: Prepare or reset worksheet
    sheet_name = "Consolidated"
    try:
        sheet.del_worksheet(sheet.worksheet(sheet_name))
    except gspread.WorksheetNotFound:
        pass

    worksheet = sheet.add_worksheet(title=sheet_name, rows="1000", cols="20")

    # Step 4: Upload Summary
    summary_df = pd.DataFrame(summary_rows, columns=["Ticker", "Total P&L", "Trades", "Wins", "Win Ratio (%)"])
    # 🔧 Convert to standard Python types (e.g., float, int, str)
    summary_df = summary_df.astype({
    "Ticker": str,
    "Total P&L": float,
    "Trades": int,
    "Wins": int,
    "Win Ratio (%)": float
   })
    worksheet.update("A1", [["Summary Report"]])
    worksheet.update("A3", [summary_df.columns.tolist()] + summary_df.values.tolist())

    # ✅ Step 5: Upload Trade Logs
    trade_df = pd.DataFrame(
    trade_logs,
    columns=["Ticker", "Buy Date", "Sell Date", "Buy Price", "Sell Price", "P&L"]
   )

    # 🔧 Fix: Convert datetime (Timestamp) columns to string for JSON serialization
    trade_df["Buy Date"] = trade_df["Buy Date"].astype(str)
    trade_df["Sell Date"] = trade_df["Sell Date"].astype(str)

    # 📌 Decide starting row after the summary ends
    start_row = len(summary_df) + 6  # Add some spacing after summary

    # 🆙 Upload header and data
    worksheet.update(f"A{start_row}", [["Trade Log"]])
    worksheet.update(
    f"A{start_row+2}",
    [trade_df.columns.tolist()] + trade_df.values.tolist()
   )

    

    print("✅ Uploaded consolidated summary and trade log to Google Sheets.")
