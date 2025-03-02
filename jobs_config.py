# jobs_config.py
from rapidfuzz import process, fuzz

# Static fallback company keywords (optional)
COMPANY_KEYWORDS = {
    "Lowes": ["lowes", "lowe's"],
    "The New IEM": ["iem", "the new iem"],
    "Epic": ["epic", "epic healthcare", "epic.com"],
    "Spectrum": ["spectrum", "charter communications"],
    "TherapyNotes": ["therapynotes", "therapy notes"],
    "MBS Professional Staffing": ["mbs professional staffing", "mbs staffing"],
    "Discover Financial Services": ["discover", "discover financial"],
}

STATUS_KEYWORDS = {
    "denied": "Denied",
    "reject": "Denied",
    "offer": "Offer",
    "interview": "Interview",
    "received": "Applied",
    "application": "Applied",
}

def parse_company(subject, body):
    """
    Attempts to extract a company name using known keywords.
    Returns the company name if found; otherwise, None.
    """
    text = (subject + " " + body).lower()
    for company, keywords in COMPANY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return company
    return None

def guess_company_name_dynamic(extracted_candidate, known_companies, cutoff=70):
    """
    Uses fuzzy matching to compare an extracted candidate against a dynamic list of companies.
    Returns (best_match, score) if a match is above the cutoff; otherwise, (None, 0).
    """
    if not extracted_candidate or not known_companies:
        return None, 0
    best_match, score, _ = process.extractOne(extracted_candidate, known_companies, scorer=fuzz.ratio)
    if score >= cutoff:
        return best_match, score
    else:
        return None, 0

def interpret_status(subject, body):
    """
    Interprets the job application status from email text.
    Returns one of "Applied", "Interview", "Offer", "Denied", or "Unknown".
    """
    text = (subject + " " + body).lower()
    for kw, status in STATUS_KEYWORDS.items():
        if kw in text:
            return status
    return "Unknown"
