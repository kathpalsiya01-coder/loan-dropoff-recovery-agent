"""
Mock FAQ / policy knowledge base for the loan application.
In a real deployment this would be the lender's actual policy docs,
KYC requirements, and objection-handling playbook.
"""

FAQ_DOCS = [
    {
        "id": "pan_card_requirement",
        "field": "pan_card",
        "text": (
            "PAN card is mandatory for all loan applications in India as per RBI KYC "
            "guidelines. It is used to verify identity and check credit history with "
            "bureaus like CIBIL. Without a valid PAN, the loan cannot be legally "
            "disbursed. Users often hesitate here because they worry about data misuse "
            "-- reassure them that PAN details are used only for KYC/credit verification "
            "and are encrypted at rest."
        ),
    },
    {
        "id": "income_proof_requirement",
        "field": "income_proof",
        "text": (
            "Income proof (salary slips for salaried applicants, last 2 years ITR for "
            "self-employed) is required to assess repayment capacity. If a user doesn't "
            "have salary slips, bank statements showing regular salary credits for the "
            "last 3 months are an acceptable alternative. Self-employed users can submit "
            "GST returns as an alternative to ITR."
        ),
    },
    {
        "id": "interest_rate_explanation",
        "field": "loan_terms",
        "text": (
            "Interest rates are personalized based on credit score, loan amount, and "
            "tenure. Rates typically range from 10.5% to 24% per annum for personal "
            "loans. A lower credit score does not disqualify a user -- it results in a "
            "higher rate reflecting risk, not a rejection. Users can also opt for a "
            "shorter tenure to reduce total interest paid, even if EMI is higher."
        ),
    },
    {
        "id": "processing_fee",
        "field": "loan_terms",
        "text": (
            "A one-time processing fee of 1-2% of the loan amount is deducted from the "
            "disbursed amount, not charged separately upfront. This is standard across "
            "lenders and is disclosed in the loan agreement before final confirmation. "
            "It is non-refundable once the loan is disbursed but not charged if the "
            "application is withdrawn before approval."
        ),
    },
    {
        "id": "aadhaar_ekyc",
        "field": "aadhaar",
        "text": (
            "Aadhaar-based eKYC lets users complete identity verification digitally "
            "using an OTP sent to their Aadhaar-linked mobile number, avoiding physical "
            "document upload. If the mobile number isn't linked to Aadhaar, users can "
            "instead upload a scanned Aadhaar copy plus a live selfie for manual "
            "verification, which takes slightly longer (usually same-day)."
        ),
    },
    {
        "id": "approval_timeline",
        "field": "general",
        "text": (
            "Most applications with complete KYC and income documents are approved "
            "within 24-48 hours. Disbursal follows within another 24 hours after final "
            "e-sign of the loan agreement. Incomplete documentation is the single "
            "biggest cause of delay -- flagging exactly which document is missing "
            "upfront significantly speeds up approval."
        ),
    },
    {
        "id": "data_privacy",
        "field": "general",
        "text": (
            "All user data (PAN, income documents, Aadhaar) is encrypted in transit and "
            "at rest, and used solely for KYC and credit assessment as mandated by RBI. "
            "Data is not sold or shared with third-party marketers. Users can request "
            "data deletion after loan closure, subject to statutory record-keeping "
            "requirements (typically 7-10 years for financial records)."
        ),
    },
]