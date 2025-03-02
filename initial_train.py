# initial_train.py
from email_classifier import IncrementalEmailClassifier

# Example initial training data (adjust these examples and labels to your needs)
labeled_emails = [
    "Your application has been received by Lowes. Thank you for applying.",
    "Interview invitation: We would like to schedule an interview for the Software Engineer position at Epic.",
    "Job Application update: Your application for the position has been reviewed.",
    "Dear customer, your invoice is attached.",
    "Spam message: Win a million dollars now!",
    "Meeting reminder: Don't forget our team meeting at 10 AM tomorrow.",
]

# Labels: 1 indicates job-related, 0 indicates not job-related.
labels = [1, 1, 1, 0, 0, 0]

# Initialize and perform initial training
classifier = IncrementalEmailClassifier()
classifier.partial_fit(labeled_emails, labels)
classifier.save()

print("Initial training complete and model saved.")
