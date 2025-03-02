# email_classifier.py
import os
import pickle
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import HashingVectorizer

MODEL_PATH = "email_classifier_inc.pkl"

class IncrementalEmailClassifier:
    def __init__(self):
        # HashingVectorizer is stateless and ideal for incremental learning.
        self.vectorizer = HashingVectorizer(stop_words='english',
                                              alternate_sign=False,
                                              n_features=2**16)
        # Using SGDClassifier with loss="log" provides probability estimates.
        self.classifier = SGDClassifier(loss="log", max_iter=5, tol=None)
        self.initialized = False
        self.classes = [0, 1]  # 0: Not job-related, 1: Job-related

    def partial_fit(self, texts, labels):
        """
        Incrementally update the classifier with new examples.
        texts: list of raw email texts.
        labels: list of corresponding labels (0 or 1).
        """
        X = self.vectorizer.transform(texts)
        if not self.initialized:
            self.classifier.partial_fit(X, labels, classes=self.classes)
            self.initialized = True
        else:
            self.classifier.partial_fit(X, labels)

    def predict(self, text):
        """
        Returns a tuple (prediction, probability) for the given text.
        """
        X = self.vectorizer.transform([text])
        pred = self.classifier.predict(X)[0]
        try:
            prob = self.classifier.predict_proba(X)[0][1]
        except AttributeError:
            prob = 1.0 if pred == 1 else 0.0
        return pred, prob

    def save(self, model_path=MODEL_PATH):
        with open(model_path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(model_path=MODEL_PATH):
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                return pickle.load(f)
        else:
            return IncrementalEmailClassifier()

def is_job_related(email_text, threshold=0.7):
    """
    Loads the incremental classifier, predicts, and returns (is_job, probability).
    """
    model = IncrementalEmailClassifier.load()
    pred, prob = model.predict(email_text)
    is_job = (pred == 1)
    if prob is None:
        prob = 1.0 if is_job else 0.0
    return is_job, prob

def update_model(email_text, label):
    """
    Incrementally updates the classifier with a new example.
    email_text: The raw email text.
    label: 1 if job-related, 0 otherwise.
    """
    model = IncrementalEmailClassifier.load()
    model.partial_fit([email_text], [label])
    model.save()
