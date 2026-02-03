"""
Creates a sample insurance FAQ PDF for testing the RAG system.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import os


def create_sample_pdf():
    """Generate a sample insurance FAQ PDF."""
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)

    pdf_path = os.path.join(data_dir, 'knowledge.pdf')

    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        spaceAfter=30,
    )
    story.append(Paragraph("Insurance Agency FAQ", title_style))
    story.append(Spacer(1, 0.3 * inch))

    # FAQ content
    faqs = [
        {
            "question": "How do I file a claim?",
            "answer": "To file a claim, you can call our 24/7 claims hotline at 1-800-CLAIM-NOW or submit a claim online through your customer portal. You will need your policy number, date and time of the incident, description of what happened, and any relevant photos or documentation. A claims adjuster will be assigned to your case within 24 hours."
        },
        {
            "question": "What is a deductible and how does it work?",
            "answer": "A deductible is the amount you pay out-of-pocket before your insurance coverage kicks in. For example, if you have a $500 deductible and file a claim for $2,000 in damages, you pay the first $500 and we cover the remaining $1,500. You pay your deductible each time you file a claim. Higher deductibles typically result in lower monthly premiums."
        },
        {
            "question": "Can I add another driver to my auto policy?",
            "answer": "Yes, you can add additional drivers to your auto insurance policy at any time. To add a driver, contact our customer service team with the driver's full name, date of birth, driver's license number, and driving history. There may be an adjustment to your premium depending on the driver's age and driving record. Household members and regular users of your vehicle should be listed on your policy."
        },
        {
            "question": "What documents do I need to provide when making a claim?",
            "answer": "When filing a claim, please provide: (1) Your insurance policy number, (2) Date, time, and location of the incident, (3) Photos of any damage, (4) Police report if applicable, (5) Contact information for any other parties involved, (6) Witness statements if available, (7) Medical records for injury claims, and (8) Repair estimates or receipts. Having these documents ready will help expedite your claim processing."
        },
        {
            "question": "How long does it take to process a claim?",
            "answer": "Most claims are processed within 7-10 business days once we receive all required documentation. Simple claims with clear liability may be resolved faster, while complex claims involving investigations or multiple parties may take longer. You can check your claim status anytime through your online portal or by calling your assigned claims adjuster directly."
        },
        {
            "question": "What is covered under my homeowners insurance?",
            "answer": "Standard homeowners insurance typically covers: (1) Dwelling coverage for the structure of your home, (2) Personal property coverage for your belongings, (3) Liability protection if someone is injured on your property, (4) Additional living expenses if you need temporary housing due to covered damage, and (5) Other structures like garages or sheds. Specific coverage limits and exclusions vary by policy, so review your policy documents or contact us for details."
        },
        {
            "question": "Are natural disasters covered?",
            "answer": "Coverage for natural disasters depends on your policy type. Standard policies typically cover fire, lightning, hail, and windstorms. However, floods and earthquakes usually require separate policies. Hurricane coverage varies by location and may have special deductibles. We recommend reviewing your policy annually to ensure you have adequate protection for natural disasters common in your area."
        },
        {
            "question": "How can I lower my insurance premium?",
            "answer": "There are several ways to reduce your premium: (1) Increase your deductible, (2) Bundle multiple policies (auto, home, life) with us for multi-policy discounts, (3) Install security systems or safety features, (4) Maintain a good credit score, (5) Ask about discounts for safe driving, being claim-free, or paying annually instead of monthly, and (6) Review your coverage annually to ensure you're not over-insured."
        }
    ]

    question_style = ParagraphStyle(
        'Question',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='darkblue',
        spaceAfter=10,
        spaceBefore=15,
    )

    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['BodyText'],
        fontSize=11,
        spaceAfter=15,
    )

    for faq in faqs:
        story.append(Paragraph(f"Q: {faq['question']}", question_style))
        story.append(Paragraph(faq['answer'], answer_style))

    # Build PDF
    doc.build(story)
    print(f"Sample PDF created at: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    create_sample_pdf()
