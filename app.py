from flask import Flask, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# --- Simplified AI and NLP Functions ---
# Note: For a hackathon demo, these rule-based functions are a great way to
# show functionality without complex setup.

def get_sentiment(text):
    """
    Analyzes sentiment based on keywords in the email body.
    This simulates a sentiment analysis model.
    """
    text_lower = text.lower()
    negative_words = ["frustrated", "cannot", "error", "down", "critical", "not working", "unable", "inaccessible", "needs immediate correction"]
    positive_words = ["thank you", "great", "excellent", "love", "good service", "satisfied"]
    
    if any(word in text_lower for word in negative_words):
        return "Negative"
    elif any(word in text_lower for word in positive_words):
        return "Positive"
    else:
        return "Neutral"

def get_priority(text):
    """
    Determines priority based on urgent keywords in the email body or subject.
    This simulates a priority classification model.
    """
    text_lower = text.lower()
    urgent_keywords = ["urgent", "immediately", "critical", "cannot access", "down", "inaccessible"]
    
    if any(word in text_lower for word in urgent_keywords):
        return "Urgent"
    else:
        return "Not Urgent"

def extract_contact_details(text):
    """
    Extracts a mock contact email from the body.
    This is a simple text search, simulating a more complex extractor.
    """
    import re
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return emails[0] if emails else "Not Found"

def generate_llm_response(subject, body):
    """
    Generates a mock LLM-style response based on keywords.
    This function simulates a sophisticated AI response generator.
    """
    combined_text = subject.lower() + " " + body.lower()
    if "billing error" in combined_text or "charged twice" in combined_text:
        return "Dear customer, we apologize for the billing error. We are investigating the issue and will issue a refund immediately. Thank you for your patience."
    elif "password" in combined_text or "reset link" in combined_text:
        return "Dear user, we understand you are having trouble with your password. Please try the 'Forgot Password' link on our login page. If the issue persists, a team member will reach out to you directly to help with the reset. We apologize for the inconvenience."
    elif "access" in combined_text or "log into my account" in combined_text or "inaccessible" in combined_text:
        return "Hello, we understand you are having issues with your account access. Our team is looking into this and will contact you shortly to resolve it. We apologize for any inconvenience this has caused."
    elif "down" in combined_text or "critical" in combined_text:
        return "Hello, we have received your critical alert regarding system downtime. Our engineering team is currently investigating this issue with the highest priority and will provide an update as soon as possible. Thank you for your patience."
    else:
        return "Hello, thank you for your query. Our team has received your request and will get back to you with a detailed response shortly. Thank you for your patience."


# --- New Route for the Dashboard Page ---
@app.route('/')
def home():
    """
    This route serves the main dashboard HTML page.
    """
    return render_template('index.html')

@app.route('/api/emails')
def get_emails():
    """
    Main API endpoint to process emails from the CSV and return JSON data.
    """
    try:
        # Load the CSV file. Replace the filename with the exact name you have.
        df = pd.read_csv('68b1acd44f393_Sample_Support_Emails_Dataset (1).csv')

        # Filter emails based on subject keywords
        filter_keywords = ["support", "query", "request", "help", "critical", "urgent", "access", "downtime"]
        df_filtered = df[df['subject'].str.contains('|'.join(filter_keywords), case=False, na=False)]

        # Process each email
        processed_emails = []
        for index, row in df_filtered.iterrows():
            sender_email = row['sender']
            subject = row['subject']
            body = row['body']
            sent_date = row['sent_date']

            # Apply our mock AI functions
            sentiment = get_sentiment(body)
            priority = get_priority(subject + " " + body)
            auto_response = generate_llm_response(subject, body)
            extracted_info = {
                "contact_details": sender_email, # Using sender email as mock contact detail
                "customer_request": body[:50] + "...", # A brief snippet of the request
                "sentiment_indicator": sentiment
            }

            processed_emails.append({
                "sender": sender_email,
                "subject": subject,
                "body": body,
                "date": sent_date,
                "priority": priority,
                "sentiment": sentiment,
                "auto_response": auto_response,
                "extracted_info": extracted_info
            })

        # Sort emails by priority (Urgent first)
        processed_emails.sort(key=lambda x: x['priority'] != 'Urgent')

        # Calculate dashboard analytics
        total_emails = len(df_filtered)
        urgent_emails = sum(1 for e in processed_emails if e['priority'] == 'Urgent')
        positive_sentiment = sum(1 for e in processed_emails if e['sentiment'] == 'Positive')
        negative_sentiment = sum(1 for e in processed_emails if e['sentiment'] == 'Negative')
        neutral_sentiment = sum(1 for e in processed_emails if e['sentiment'] == 'Neutral')

        stats = {
            "total_emails": total_emails,
            "urgent_emails": urgent_emails,
            "sentiment_counts": {
                "Positive": positive_sentiment,
                "Negative": negative_sentiment,
                "Neutral": neutral_sentiment
            }
        }
        
        return jsonify({"emails": processed_emails, "stats": stats})

    except FileNotFoundError:
        return jsonify({"error": "CSV file not found. Please ensure '68b1acd44f393_Sample_Support_Emails_Dataset (1).csv' is in the same directory as app.py"}), 404

if __name__ == '__main__':
    app.run(debug=True)
