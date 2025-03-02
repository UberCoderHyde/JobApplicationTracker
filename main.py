# main.py
import datetime
from gmail_utils import gmail_authenticate, get_unread_emails, mark_email_as_read
from sheets_utils import update_application_status, append_new_row, get_all_companies
from jobs_config import parse_company, interpret_status, guess_company_name_dynamic
from email_classifier import is_job_related, update_model

def main():
    # Authenticate with Gmail
    service = gmail_authenticate()

    # Fetch unread emails
    emails = get_unread_emails(service)
    if not emails:
        print("No new unread emails to process.")
        return

    # Get dynamic list of existing companies from the Google Sheet
    sheet_name = "Job Application Tracker"
    existing_companies = get_all_companies(sheet_name)

    for mail in emails:
        subject = mail['subject']
        body = mail['body']
        full_text = subject + " " + body

        # Classify email using the incremental classifier
        is_job, probability = is_job_related(full_text)
        print(f"Email '{subject}' classified as job-related: {is_job} (confidence: {probability:.2f})")
        
        # --- Begin Interactive Feedback Section ---
        user_input = input("Was this classification correct? (y/n) or press Enter to skip: ").strip().lower()
        if user_input == "y":
            # Prediction is correct; update model with same label.
            label = 1 if is_job else 0
            update_model(full_text, label)
            print("Model updated with your feedback.")
        elif user_input == "n":
            # Prediction is incorrect; update model with the opposite label.
            label = 0 if is_job else 1
            update_model(full_text, label)
            print("Model updated with corrected feedback.")
        else:
            print("No feedback provided; model not updated.")
        # --- End Interactive Feedback Section ---

        # Skip further processing if not job-related.
        if not is_job:
            print("Skipping non-job email.")
            mark_email_as_read(service, mail['id'])
            continue

        # First, try keyword-based extraction of company name.
        company_name = parse_company(subject, body)
        if not company_name:
            # Fallback: extract a candidate (e.g., the first word in the subject).
            extracted_candidate = subject.split()[0]
            guessed, score = guess_company_name_dynamic(extracted_candidate, existing_companies)
            if guessed:
                company_name = guessed
                print(f"Fuzzy match found: '{company_name}' (score: {score})")
            else:
                company_name = extracted_candidate  # Treat as new company.
                print(f"No fuzzy match; using '{company_name}' as new company.")

        # Interpret the status of the email.
        status = interpret_status(subject, body)
        print(f"Processing email from: {mail['from']}")
        print(f"Company: {company_name}, Status: {status}")

        # Set applied date if status is "Applied".
        date_applied = None
        if status == "Applied":
            date_applied = datetime.datetime.now().strftime("%m/%d/%Y")

        # Update an existing row; if not found, append a new row.
        updated = update_application_status(sheet_name, company_name, status, date_applied)
        if not updated:
            append_new_row(sheet_name, job_title="(Unknown Title)", company_name=company_name,
                           status=status, date_applied=date_applied, notes=body[:100])
            print(f"Appended new row for '{company_name}'.")
        else:
            print(f"Updated row for '{company_name}'.")

        # Mark email as read so it won’t be reprocessed.
        mark_email_as_read(service, mail['id'])

if __name__ == "__main__":
    main()
