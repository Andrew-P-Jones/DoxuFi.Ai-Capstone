RED_FLAGS = {
    # --- Predatory Lending & High Interest ---
    "triple-digit apr": 90,
    "exceeding 300%": 95,
    "guaranteed approval": 70,
    "no credit check": 60,
    "same-day funding": 40,
    "daily repayment": 80,
    "weekly installments": 70,
    
    # --- Hidden Fees & Penalties ---
    "prepayment penalty": 50,
    "origination fee": 20,
    "junk fees": 40,
    "administrative surcharge": 25,
    "non-refundable deposit": 30,
    "yield-spread premium": 45,
    
    # --- Dangerous Structural Clauses ---
    "automatic acceleration": 85, # Entire balance due immediately on one slip-up
    "balloon payment": 75, # Massive final payment you might not afford
    "cross-default": 65, # Defaulting on this loan triggers default on others
    "automatic renewal": 40,
    "evergreen clause": 40,
    "negative amortization": 90, # Debt grows even if you pay
    "unlimited liability": 80,
    "no liability cap": 70,
    
    # --- Collateral & Rights Seizure ---
    "confession of judgment": 95, # You give up the right to defend yourself in court
    "security interest in all assets": 75,
    "auto title collateral": 80,
    "right of set-off": 50, # Lender can take money directly from your bank account
    "irrevocable power of attorney": 85,
    
    # --- Dispute & Transparency Issues ---
    "mandatory arbitration": 50,
    "class action waiver": 55,
    "choice of venue": 30, # Forced to sue them in a different state/country
    "reasonable efforts": 15, # Vague wording that avoids hard promises
    "as is basis": 40,
    "waives all notice": 70,
    "oral representations": 35 # "What the salesman said doesn't count" clauses
}

# MORE PHRASES TO EXPAND THE RISK ANALYSIS CAPABILITIES
ADDITIONAL_RED_FLAGS = {
    # --- Repayment Traps & Cycling ---
    "loan flipping": 85,           # Repeatedly refinancing to generate fees
    "equity stripping": 90,        # Lending based on asset value rather than ability to pay
    "interest-only payments": 50,  # Principal never goes down
    "mandatory payroll deduction": 60,
    "post-dated check": 70,        # Standard predatory payday practice
    "recurring ach authorization": 45,
    "automatic debit": 40,

    # --- Deceptive Disclosures ---
    "unlicensed lender": 95,
    "good faith estimate omitted": 65,
    "blank spaces": 80,            # Signing a doc with empty fields is a massive red flag
    "bait and switch": 75,
    "hidden finance charge": 60,
    "nominal rate only": 40,        # Hiding the actual APR
    "understated apr": 85,

    # --- Aggressive Legal Remedies ---
    "waiver of right to sue": 70,
    "consent to jurisdiction": 30, # Forcing you to defend yourself in a far-off state
    "attorney-in-fact for borrower": 80,
    "unilateral modification": 65, # They can change the contract whenever they want
    "reservation of rights": 25,
    "liquidated damages": 50,      # Pre-set massive fines for minor breaches
    "right of rescission waived": 90, # Illegal in many consumer contexts

    # --- Shady Marketing & Behavior ---
    "limited time offer only today": 35, # High-pressure sales tactic
    "door-to-door solicitation": 50,
    "guaranteed approval regardless of credit": 75,
    "bad credit welcome": 60,
    "tax refund anticipation": 45,
    "car title required": 80,
    
    # --- Insurance & Packaging ---
    "single premium credit insurance": 65, # Folding expensive insurance into the loan
    "bundled services": 30,
    "mandatory club membership": 40,
    "administrative surcharge": 25,
    "processing points": 45
}

# Merge them into your main dictionary
RED_FLAGS.update(ADDITIONAL_RED_FLAGS)


# ===================================================================================================

def calculate_risk_score(legal_text: str) -> dict:
    """
    Scans text for the redefined 30+ red flags.
    """
    text_lower = legal_text.lower()
    total_score = 0
    detected = []

    for phrase, weight in RED_FLAGS.items():
        if phrase in text_lower:
            total_score += weight
            detected.append({"phrase": phrase, "impact": weight})

    # Normalize score to 0-100
    normalized_score = min(total_score, 100)
    
    return {
        "risk_score": normalized_score,
        "flags_found": detected,
        "severity": "CRITICAL" if normalized_score > 80 else "HIGH" if normalized_score > 50 else "LOW"
    }