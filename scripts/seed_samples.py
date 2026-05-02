"""
scripts/seed_samples.py

Loads built-in sample regulation data directly into the database.
Use this if you don't have an Anthropic API key yet, or just want
to see the dashboard working immediately.

    python scripts/seed_samples.py
"""

import sys
import os
import json
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_FOLDER = "data"
DB_FILE     = os.path.join(DATA_FOLDER, "trade.db")

# Pre-built profiles for all 20 Asia-Pacific economies.
# These mirror what Claude AI would extract from real documents.
SAMPLE_DATA = [
    {
        "country": "Singapore", "organization": "IMDA / PDPC",
        "summary": "Singapore operates one of the most open digital trade environments in Asia. Zero tariffs, no data localization, strong e-signature law, and a network of Digital Economy Agreements make it the region's premier digital trade hub.",
        "openness_score": 8.5,
        "key_laws": ["PDPA", "Electronic Transactions Act", "Computer Misuse Act"],
        "notable_features": ["No data localization requirement", "Zero digital tariffs", "ASEAN Single Window leader"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No data localization requirement. Data may be stored anywhere with adequate protection."},
            "Cross-Border Data Flows":    {"status": "Open",              "strictness": "Low",    "details": "Transfers permitted with contractual safeguards. No government whitelist required."},
            "E-Commerce Rules":           {"status": "Comprehensive",     "strictness": "Low",    "details": "Electronic Transactions Act gives e-commerce full legal recognition."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Low",    "details": "E-signatures have the same legal effect as handwritten signatures."},
            "Consumer Protection":        {"status": "Strong",            "strictness": "Medium", "details": "CPFTA and PDPA together protect online consumers effectively."},
            "Customs & Tariffs":          {"status": "Zero",              "strictness": "Low",    "details": "Zero customs duties on all electronic transmissions."},
            "Intellectual Property":      {"status": "Strong Protection", "strictness": "Medium", "details": "Copyright Act covers digital works and anti-circumvention."},
            "Cybersecurity Requirements": {"status": "Mandatory",         "strictness": "Medium", "details": "Cybersecurity Act mandates reporting for critical information infrastructure."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law", "strictness": "Medium", "details": "PDPA governs all personal data handling. Fines up to SGD 1 million."},
            "Platform Regulations":       {"status": "Partial",           "strictness": "Low",    "details": "Online Safety Act covers harmful content. Light touch on platforms generally."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "MAS regulates digital payment tokens and fintech firms."},
            "Trade Facilitation":         {"status": "Advanced",          "strictness": "Low",    "details": "Leads ASEAN Single Window. Fully paperless customs."},
        }
    },
    {
        "country": "Thailand", "organization": "ETDA",
        "summary": "Thailand modernized its digital framework significantly in 2022 with PDPA coming into force. No data localization. Active in ASEAN Single Window. Financial sector data has partial localization rules.",
        "openness_score": 6.5,
        "key_laws": ["PDPA B.E. 2562", "Electronic Transactions Act", "Computer Crimes Act"],
        "notable_features": ["PDPA in force since 2022", "ASEAN Single Window member", "Partial financial data rules"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No blanket localization. Bank of Thailand requires certain financial data onshore."},
            "Cross-Border Data Flows":    {"status": "Conditional",       "strictness": "Medium", "details": "PDPA permits transfers with adequate protection or consent."},
            "E-Commerce Rules":           {"status": "Comprehensive",     "strictness": "Medium", "details": "Electronic Transactions Act covers contracts, signatures, and records."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Low",    "details": "ETDA certifies digital signature providers. E-signatures are legally valid."},
            "Consumer Protection":        {"status": "Moderate",          "strictness": "Medium", "details": "Consumer Protection Act extends to online transactions."},
            "Customs & Tariffs":          {"status": "Moderate",          "strictness": "Medium", "details": "Average ICT tariff ~10%. Member of ATIGA for ASEAN goods."},
            "Intellectual Property":      {"status": "Moderate",          "strictness": "Medium", "details": "Copyright Act covers digital works but enforcement is inconsistent."},
            "Cybersecurity Requirements": {"status": "Mandatory",         "strictness": "Medium", "details": "Cybersecurity Act 2019 mandates reporting for critical sectors."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law", "strictness": "Medium", "details": "PDPA covers collection, use, and disclosure of personal data."},
            "Platform Regulations":       {"status": "Partial",           "strictness": "Medium", "details": "Computer Crimes Act requires content removal on request."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "Bank of Thailand regulates digital payment services and e-money."},
            "Trade Facilitation":         {"status": "Moderate",          "strictness": "Low",    "details": "National Single Window operational. Connected to ASEAN Single Window."},
        }
    },
    {
        "country": "Japan", "organization": "METI",
        "summary": "Japan champions Data Free Flow with Trust (DFFT) globally. APPI provides strong privacy protection with open cross-border transfer rules. CPTPP and RCEP membership bring strong digital trade commitments. Zero digital tariffs.",
        "openness_score": 7.5,
        "key_laws": ["APPI", "Electronic Signatures Act", "Unfair Competition Prevention Act"],
        "notable_features": ["DFFT initiative leader", "CPTPP & RCEP member", "Zero digital tariffs"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No data localization. APPI allows cross-border transfers with appropriate safeguards."},
            "Cross-Border Data Flows":    {"status": "Open",              "strictness": "Low",    "details": "Open flows. Adequacy agreement with EU. DFFT initiative promotes trusted flows globally."},
            "E-Commerce Rules":           {"status": "Comprehensive",     "strictness": "Low",    "details": "Electronic Commerce Act and APPI together provide strong e-commerce framework."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Low",    "details": "Electronic Signatures Act gives digital signatures full legal effect."},
            "Consumer Protection":        {"status": "Strong",            "strictness": "Medium", "details": "Consumer Contract Act and Act on Specified Commercial Transactions cover online sales."},
            "Customs & Tariffs":          {"status": "Zero",              "strictness": "Low",    "details": "Zero customs duties on electronic transmissions. Supports WTO moratorium."},
            "Intellectual Property":      {"status": "Strong Protection", "strictness": "Medium", "details": "Copyright Act covers digital content. Strong anti-circumvention provisions."},
            "Cybersecurity Requirements": {"status": "Mandatory",         "strictness": "Medium", "details": "Cybersecurity Basic Act mandates reporting for critical infrastructure."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law", "strictness": "Medium", "details": "APPI amended 2022. EU adequacy decision in place. Strong enforcement by PPC."},
            "Platform Regulations":       {"status": "Partial",           "strictness": "Low",    "details": "Act on Improving Transparency of Digital Platforms targets major platforms."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "FSA regulates digital payments, crypto assets, and fintech."},
            "Trade Facilitation":         {"status": "Advanced",          "strictness": "Low",    "details": "Advanced paperless customs. Single Window operational."},
        }
    },
    {
        "country": "India", "organization": "MEITY",
        "summary": "India has strong data localization requirements for payments (RBI mandate) and new DPDPA 2023 restricts cross-border transfers via government whitelist. High digital tariffs. Not a RCEP or CPTPP member.",
        "openness_score": 4.0,
        "key_laws": ["DPDPA 2023", "IT Act 2000", "RBI Payment Data Localization Rules"],
        "notable_features": ["Payment data must remain in India", "Government whitelist for data transfers", "100% FDI in B2B e-commerce only"],
        "topics": {
            "Data Localization":          {"status": "Required (Payments)","strictness": "High",   "details": "RBI mandates all payment data stored only in India. DPDPA adds further restrictions."},
            "Cross-Border Data Flows":    {"status": "Restricted",         "strictness": "High",   "details": "DPDPA 2023 requires Central Government approval for transfer destinations."},
            "E-Commerce Rules":           {"status": "Partial",            "strictness": "High",   "details": "FDI rules prohibit inventory-based model for foreign companies. Complex compliance."},
            "Digital Signatures":         {"status": "Legally Recognized", "strictness": "Medium", "details": "IT Act recognizes electronic signatures. Controller of Certifying Authorities oversees."},
            "Consumer Protection":        {"status": "Moderate",           "strictness": "Medium", "details": "Consumer Protection Act 2019 covers e-commerce. Rules introduced in 2020."},
            "Customs & Tariffs":          {"status": "High",               "strictness": "High",   "details": "India levies high tariffs on digital goods. Opposes WTO moratorium on digital duties."},
            "Intellectual Property":      {"status": "Moderate",           "strictness": "Medium", "details": "Copyright Act covers digital works but enforcement remains challenging."},
            "Cybersecurity Requirements": {"status": "Mandatory",          "strictness": "High",   "details": "CERT-In mandates 6-hour breach reporting. Strict data retention rules."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law",  "strictness": "High",   "details": "DPDPA 2023 enacted. Government retains broad exemptions. Rules pending."},
            "Platform Regulations":       {"status": "Comprehensive",      "strictness": "High",   "details": "IT Rules 2021 impose significant obligations on social media and OTT platforms."},
            "Financial Digital Services": {"status": "Regulated",          "strictness": "High",   "details": "RBI regulates payments tightly. All payment data must stay in India."},
            "Trade Facilitation":         {"status": "Moderate",           "strictness": "Medium", "details": "ICEGATE provides electronic customs filing. Single Window improving."},
        }
    },
    {
        "country": "Australia", "organization": "DFAT",
        "summary": "Australia is a strong advocate for open digital trade in the Asia-Pacific. CPTPP and RCEP member. No data localization. Privacy Act reforms underway. Supports WTO zero-tariff moratorium.",
        "openness_score": 7.5,
        "key_laws": ["Privacy Act 1988", "Electronic Transactions Act", "Online Safety Act 2021"],
        "notable_features": ["CPTPP & RCEP member", "No data localization", "Digital Economy Agreements with Singapore"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No data localization. Data may be stored offshore with appropriate security."},
            "Cross-Border Data Flows":    {"status": "Open",              "strictness": "Low",    "details": "Privacy Act permits cross-border transfers with comparable protection."},
            "E-Commerce Rules":           {"status": "Comprehensive",     "strictness": "Low",    "details": "Electronic Transactions Act provides robust e-commerce framework."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Low",    "details": "Electronic Transactions Act gives e-signatures full legal effect."},
            "Consumer Protection":        {"status": "Strong",            "strictness": "Medium", "details": "Australian Consumer Law extends to online markets and digital products."},
            "Customs & Tariffs":          {"status": "Zero",              "strictness": "Low",    "details": "Zero tariffs on electronic transmissions. Supports permanent WTO moratorium."},
            "Intellectual Property":      {"status": "Strong Protection", "strictness": "Medium", "details": "Copyright Act covers digital works with CPTPP-aligned provisions."},
            "Cybersecurity Requirements": {"status": "Mandatory",         "strictness": "Medium", "details": "Security of Critical Infrastructure Act mandates reporting and risk management."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law", "strictness": "Medium", "details": "Privacy Act under review. Major reform expected to strengthen enforcement."},
            "Platform Regulations":       {"status": "Partial",           "strictness": "Medium", "details": "Online Safety Act addresses harmful content. News Media Bargaining Code targets platforms."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "ASIC and APRA regulate fintech. Payments system under reform."},
            "Trade Facilitation":         {"status": "Advanced",          "strictness": "Low",    "details": "Single Window operational. Paperless customs for most trade."},
        }
    },
    {
        "country": "Vietnam", "organization": "MOIT",
        "summary": "Vietnam has data localization requirements under the Cybersecurity Law and is implementing PDPA-style rules. CPTPP and RCEP membership provide some open trade commitments that partially offset domestic restrictions.",
        "openness_score": 5.5,
        "key_laws": ["Cybersecurity Law 2018", "Law on E-Transactions", "Decree 13/2023"],
        "notable_features": ["Cybersecurity Law mandates localization", "CPTPP & RCEP member", "Growing digital economy"],
        "topics": {
            "Data Localization":          {"status": "Sector-specific",   "strictness": "High",   "details": "Cybersecurity Law requires localization for data related to critical infrastructure."},
            "Cross-Border Data Flows":    {"status": "Conditional",       "strictness": "High",   "details": "Transfers require government approval for specified categories of data."},
            "E-Commerce Rules":           {"status": "Partial",           "strictness": "Medium", "details": "E-Commerce Law covers online trading. Platforms must register with Ministry."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Medium", "details": "Law on E-Transactions recognizes digital signatures. CA system in place."},
            "Consumer Protection":        {"status": "Moderate",          "strictness": "Medium", "details": "Consumer Protection Law applies online. Ministry oversight of e-commerce platforms."},
            "Customs & Tariffs":          {"status": "Moderate",          "strictness": "Medium", "details": "Average digital goods tariff ~10%. CPTPP reduces tariffs with members."},
            "Intellectual Property":      {"status": "Moderate",          "strictness": "Medium", "details": "IP Law covers digital works. CPTPP required stronger enforcement provisions."},
            "Cybersecurity Requirements": {"status": "Mandatory",         "strictness": "High",   "details": "Cybersecurity Law imposes strict requirements on online platforms and CII operators."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law", "strictness": "High",   "details": "Decree 13/2023 sets data protection rules. Strong localization component."},
            "Platform Regulations":       {"status": "Comprehensive",     "strictness": "High",   "details": "Platforms must store data locally, comply with removal requests within 24 hours."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "State Bank regulates e-payment and fintech. Sandbox program launched."},
            "Trade Facilitation":         {"status": "Moderate",          "strictness": "Low",    "details": "National Single Window operational. ASEAN Single Window connected."},
        }
    },
    {
        "country": "Indonesia", "organization": "Kominfo",
        "summary": "Indonesia passed the Personal Data Protection Law in 2022, its first comprehensive data law. Data localization applies to strategic sectors. RCEP member but high tariffs remain a barrier.",
        "openness_score": 5.0,
        "key_laws": ["PDP Law 2022", "Government Regulation 71/2019", "Electronic Information & Transactions Law"],
        "notable_features": ["Sector-based data localization", "PDP Law 2022 — first comprehensive law", "Largest ASEAN economy"],
        "topics": {
            "Data Localization":          {"status": "Sector-specific",   "strictness": "High",   "details": "GR 71/2019 requires strategic sector data to be stored in Indonesia."},
            "Cross-Border Data Flows":    {"status": "Restricted",        "strictness": "High",   "details": "Transfers require coordination center in Indonesia for electronic system operators."},
            "E-Commerce Rules":           {"status": "Partial",           "strictness": "Medium", "details": "Government Regulation 80/2019 covers e-commerce. Registration required for platforms."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Medium", "details": "ITE Law recognizes e-signatures. Certified Electronic Certification Organizers issue certs."},
            "Consumer Protection":        {"status": "Moderate",          "strictness": "Medium", "details": "Consumer Protection Law applies online. OJK regulates financial consumer protection."},
            "Customs & Tariffs":          {"status": "High",              "strictness": "High",   "details": "Average tariff ~15% on digital goods. De minimis threshold recently changed."},
            "Intellectual Property":      {"status": "Moderate",          "strictness": "Medium", "details": "Copyright Law covers digital works. Enforcement improving but gaps remain."},
            "Cybersecurity Requirements": {"status": "Mandatory",         "strictness": "High",   "details": "BSSN (National Cyber Agency) oversees cybersecurity. Incident reporting required."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law", "strictness": "High",   "details": "PDP Law 2022 establishes rights and obligations. Implementation ongoing."},
            "Platform Regulations":       {"status": "Comprehensive",     "strictness": "High",   "details": "Platforms must register and comply with content takedown requirements within 24 hours."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "OJK and Bank Indonesia regulate digital financial services and payment systems."},
            "Trade Facilitation":         {"status": "Moderate",          "strictness": "Low",    "details": "Indonesia NSW operational. Connected to ASEAN Single Window."},
        }
    },
    {
        "country": "South Korea", "organization": "MSIT",
        "summary": "South Korea has a mature digital trade framework with PIPA providing strong privacy protection. No data localization. RCEP member. Strong cybersecurity rules. Zero digital tariffs.",
        "openness_score": 7.0,
        "key_laws": ["PIPA", "Electronic Signature Act", "Network Act"],
        "notable_features": ["Strong PIPA enforcement", "RCEP member", "Zero digital tariffs"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No data localization requirement. Cross-border transfers permitted with safeguards."},
            "Cross-Border Data Flows":    {"status": "Open",              "strictness": "Low",    "details": "PIPA allows transfers with consent or contractual safeguards."},
            "E-Commerce Rules":           {"status": "Comprehensive",     "strictness": "Low",    "details": "E-Commerce Consumer Protection Act and PIPA together cover online commerce."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Low",    "details": "Electronic Signature Act gives e-signatures full legal validity."},
            "Consumer Protection":        {"status": "Strong",            "strictness": "Medium", "details": "E-Commerce Consumer Protection Act provides strong online buyer rights."},
            "Customs & Tariffs":          {"status": "Zero",              "strictness": "Low",    "details": "Zero customs duties on electronic transmissions."},
            "Intellectual Property":      {"status": "Strong Protection", "strictness": "Medium", "details": "Copyright Act covers digital works. Strong enforcement by Korea Copyright Commission."},
            "Cybersecurity Requirements": {"status": "Mandatory",         "strictness": "High",   "details": "Network Act and Information Security Industry Act require extensive security measures."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law", "strictness": "High",   "details": "PIPA among Asia's strongest data protection laws. Active enforcement by PIPC."},
            "Platform Regulations":       {"status": "Partial",           "strictness": "Medium", "details": "Platform regulations evolving. Online Platform Intermediary Act under discussion."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "FSC and FSS regulate fintech. Electronic Financial Transactions Act covers digital payments."},
            "Trade Facilitation":         {"status": "Advanced",          "strictness": "Low",    "details": "uTradeHub provides paperless trade. Single Window operational."},
        }
    },
    {
        "country": "Malaysia", "organization": "MCMC",
        "summary": "Malaysia has a modern PDPA and active e-commerce sector. No data localization. RCEP member. MSC status zones provide special digital trade incentives. Reasonable tariff environment.",
        "openness_score": 7.0,
        "key_laws": ["PDPA 2010", "Digital Signature Act 1997", "Computer Crimes Act 1997"],
        "notable_features": ["No data localization", "RCEP member", "MSC Malaysia digital corridor"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "PDPA does not impose localization. Data may be transferred offshore with consent."},
            "Cross-Border Data Flows":    {"status": "Open",              "strictness": "Low",    "details": "Transfers permitted with data subject consent or equivalent protection."},
            "E-Commerce Rules":           {"status": "Partial",           "strictness": "Low",    "details": "Consumer Protection Act and PDPA cover online trade. Dedicated e-commerce law absent."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Low",    "details": "Digital Signature Act 1997 gives digital signatures full legal recognition."},
            "Consumer Protection":        {"status": "Moderate",          "strictness": "Medium", "details": "Consumer Protection Act extended to online transactions."},
            "Customs & Tariffs":          {"status": "Low",               "strictness": "Low",    "details": "Low tariffs on most digital goods. ATIGA removes tariffs for ASEAN trade."},
            "Intellectual Property":      {"status": "Moderate",          "strictness": "Medium", "details": "Copyright Act covers digital works. Enforcement improving."},
            "Cybersecurity Requirements": {"status": "Mandatory",         "strictness": "Medium", "details": "National Cyber Security Agency coordinates. CII operators face mandatory requirements."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law", "strictness": "Medium", "details": "PDPA 2010 in force. Amendment to strengthen it underway."},
            "Platform Regulations":       {"status": "Partial",           "strictness": "Low",    "details": "Communications and Multimedia Act covers online content. Light touch generally."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "BNM regulates e-money, digital banks, and payment systems. Sandbox available."},
            "Trade Facilitation":         {"status": "Moderate",          "strictness": "Low",    "details": "Malaysia NSW operational. ASEAN Single Window connected."},
        }
    },
    {
        "country": "Philippines", "organization": "NPC",
        "summary": "Philippines has a comprehensive Data Privacy Act and no data localization. RCEP member. Growing e-commerce sector. National Privacy Commission actively enforces rules.",
        "openness_score": 5.5,
        "key_laws": ["Data Privacy Act 2012", "Electronic Commerce Act 2000", "Cybercrime Prevention Act 2012"],
        "notable_features": ["No data localization", "Active NPC enforcement", "ASEAN Single Window member"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No data localization requirement under the Data Privacy Act."},
            "Cross-Border Data Flows":    {"status": "Conditional",       "strictness": "Medium", "details": "Cross-border transfers require comparable data protection at destination."},
            "E-Commerce Rules":           {"status": "Partial",           "strictness": "Medium", "details": "Electronic Commerce Act covers contracts and signatures. DTI regulates online trade."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Low",    "details": "Electronic Commerce Act gives e-signatures legal recognition."},
            "Consumer Protection":        {"status": "Moderate",          "strictness": "Medium", "details": "Consumer Act and DTI rules cover online consumers."},
            "Customs & Tariffs":          {"status": "Moderate",          "strictness": "Medium", "details": "Average tariff ~10%. ATIGA for ASEAN goods. De minimis threshold low."},
            "Intellectual Property":      {"status": "Moderate",          "strictness": "Medium", "details": "IP Code covers digital works. Enforcement improving."},
            "Cybersecurity Requirements": {"status": "Mandatory",         "strictness": "Medium", "details": "Cybercrime Prevention Act and NPC rules require security measures and breach reporting."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law", "strictness": "Medium", "details": "Data Privacy Act 2012. NPC is active enforcer with investigative powers."},
            "Platform Regulations":       {"status": "Partial",           "strictness": "Medium", "details": "Social Media Act under discussion. Current rules are light touch."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "BSP regulates e-money and digital banks. Very high mobile money adoption."},
            "Trade Facilitation":         {"status": "Moderate",          "strictness": "Low",    "details": "PhilTradeNet Single Window operational."},
        }
    },
    {
        "country": "New Zealand", "organization": "MFAT",
        "summary": "New Zealand has a strong Privacy Act 2020 and open digital trade policy. CPTPP founding member. Zero digital tariffs. Actively pursues digital economy agreements.",
        "openness_score": 7.5,
        "key_laws": ["Privacy Act 2020", "Electronic Transactions Act 2002", "Copyright Act 1994"],
        "notable_features": ["CPTPP founding member", "Zero digital tariffs", "Strong Privacy Act 2020"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No localization requirement. Privacy Act allows offshore storage with safeguards."},
            "Cross-Border Data Flows":    {"status": "Open",              "strictness": "Low",    "details": "Privacy Act permits transfers to countries with comparable protection."},
            "E-Commerce Rules":           {"status": "Comprehensive",     "strictness": "Low",    "details": "Electronic Transactions Act provides solid e-commerce framework."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Low",    "details": "Electronic Transactions Act gives e-signatures full legal effect."},
            "Consumer Protection":        {"status": "Strong",            "strictness": "Medium", "details": "Consumer Guarantees Act and Fair Trading Act cover online commerce."},
            "Customs & Tariffs":          {"status": "Zero",              "strictness": "Low",    "details": "Zero customs duties on digital goods. Supports WTO moratorium."},
            "Intellectual Property":      {"status": "Strong Protection", "strictness": "Medium", "details": "Copyright Act covers digital works with CPTPP-aligned provisions."},
            "Cybersecurity Requirements": {"status": "Voluntary",         "strictness": "Low",    "details": "GCSB provides guidance. Critical infrastructure rules apply but lighter touch."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law", "strictness": "Medium", "details": "Privacy Act 2020 modernized framework. OPC actively enforces."},
            "Platform Regulations":       {"status": "Partial",           "strictness": "Low",    "details": "Harmful Digital Communications Act covers cyberbullying. Light platform rules."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Low",    "details": "RBNZ and FMA regulate payments and fintech. Sandbox available."},
            "Trade Facilitation":         {"status": "Advanced",          "strictness": "Low",    "details": "Customs fully electronic. Single Window operational."},
        }
    },
    {
        "country": "China", "organization": "MIIT",
        "summary": "China has broad data localization requirements, internet content restrictions, and high digital tariffs. RCEP membership provides some regional openness. Strict regulatory environment for all digital trade.",
        "openness_score": 3.5,
        "key_laws": ["PIPL", "Cybersecurity Law", "Data Security Law", "Cross-Border Data Transfer Rules"],
        "notable_features": ["Broad data localization", "Government approval for data exports", "Largest RCEP economy"],
        "topics": {
            "Data Localization":          {"status": "Required",           "strictness": "High",   "details": "CIIOs must store important data in China. PIPL extends rules broadly."},
            "Cross-Border Data Flows":    {"status": "Restricted",         "strictness": "High",   "details": "Security assessments, SCCs, or certification required for most cross-border transfers."},
            "E-Commerce Rules":           {"status": "Comprehensive",      "strictness": "High",   "details": "E-Commerce Law requires platform registration, disclosure, and data retention."},
            "Digital Signatures":         {"status": "Legally Recognized", "strictness": "Medium", "details": "Electronic Signature Law gives digital signatures legal effect. CA system regulated."},
            "Consumer Protection":        {"status": "Strong",             "strictness": "High",   "details": "E-Commerce Law and Consumer Protection Law together provide strong consumer rights."},
            "Customs & Tariffs":          {"status": "High",               "strictness": "High",   "details": "High tariffs on many digital goods. Opposes permanent WTO moratorium."},
            "Intellectual Property":      {"status": "Strong Protection",  "strictness": "High",   "details": "Copyright Law covers digital works. IP enforcement has strengthened significantly."},
            "Cybersecurity Requirements": {"status": "Mandatory",          "strictness": "High",   "details": "Cybersecurity Law imposes extensive requirements. CII operators face strictest rules."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law",  "strictness": "High",   "details": "PIPL, DSL, and Cybersecurity Law together create a complex overlapping framework."},
            "Platform Regulations":       {"status": "Comprehensive",      "strictness": "High",   "details": "Extensive platform rules including algorithm regulation, recommendation systems, and content."},
            "Financial Digital Services": {"status": "Regulated",          "strictness": "High",   "details": "PBOC tightly regulates fintech. Ant Group restructure showed regulatory reach."},
            "Trade Facilitation":         {"status": "Moderate",           "strictness": "Medium", "details": "Customs Single Window operational but separate from ASEAN systems."},
        }
    },
    {
        "country": "Hong Kong", "organization": "InvestHK",
        "summary": "Hong Kong operates as a free port with zero tariffs, open data flows, and strong rule of law. PDPO provides data protection without localization. Premier financial hub. Connected to China but separate customs territory.",
        "openness_score": 8.0,
        "key_laws": ["PDPO", "Electronic Transactions Ordinance", "Competition Ordinance"],
        "notable_features": ["Free port — zero tariffs", "No data localization", "Separate customs territory from China"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "PDPO does not require data localization. Free data flows are the norm."},
            "Cross-Border Data Flows":    {"status": "Open",              "strictness": "Low",    "details": "Data may flow freely. PDPO allows transfers with adequate protection."},
            "E-Commerce Rules":           {"status": "Comprehensive",     "strictness": "Low",    "details": "Electronic Transactions Ordinance and common law provide robust e-commerce framework."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Low",    "details": "Electronic Transactions Ordinance gives e-signatures legal effect."},
            "Consumer Protection":        {"status": "Strong",            "strictness": "Medium", "details": "Trade Descriptions Ordinance and Consumer Council protect online buyers."},
            "Customs & Tariffs":          {"status": "Zero",              "strictness": "Low",    "details": "Free port. Zero tariffs on virtually all goods and electronic transmissions."},
            "Intellectual Property":      {"status": "Strong Protection", "strictness": "Medium", "details": "Copyright Ordinance covers digital works. Strong IP enforcement."},
            "Cybersecurity Requirements": {"status": "Mandatory",         "strictness": "Medium", "details": "Cybersecurity Law (2023) extended from mainland. CII rules apply."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law", "strictness": "Medium", "details": "PDPO administered by PCPD. Significant reform underway to strengthen enforcement."},
            "Platform Regulations":       {"status": "Partial",           "strictness": "Low",    "details": "Light platform regulation. National Security Law has some content implications."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "HKMA regulates digital banks and stored value facilities. Sandbox available."},
            "Trade Facilitation":         {"status": "Advanced",          "strictness": "Low",    "details": "Paperless trade well developed. TradeLink system connects traders."},
        }
    },
    {
        "country": "Taiwan", "organization": "MOEAIC",
        "summary": "Taiwan has a mature PDPA and strong tech manufacturing sector. Zero digital tariffs. No data localization. Limited formal trade agreement participation but strong bilateral trade relationships.",
        "openness_score": 7.5,
        "key_laws": ["PDPA", "Electronic Signatures Act", "Cybersecurity Management Act"],
        "notable_features": ["Zero digital tariffs", "Advanced semiconductor sector", "No data localization"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No localization requirements. PDPA allows offshore processing with agreements."},
            "Cross-Border Data Flows":    {"status": "Open",              "strictness": "Low",    "details": "Transfers permitted with appropriate contractual safeguards."},
            "E-Commerce Rules":           {"status": "Comprehensive",     "strictness": "Low",    "details": "Consumer Protection Act and PDPA together cover e-commerce effectively."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Low",    "details": "Electronic Signatures Act gives e-signatures full legal effect."},
            "Consumer Protection":        {"status": "Strong",            "strictness": "Medium", "details": "Consumer Protection Act covers online transactions and unfair trade practices."},
            "Customs & Tariffs":          {"status": "Zero",              "strictness": "Low",    "details": "Zero tariffs on electronic transmissions. WTO moratorium supported."},
            "Intellectual Property":      {"status": "Strong Protection", "strictness": "Medium", "details": "Copyright Act covers digital works. TIPO actively enforces IP rights."},
            "Cybersecurity Requirements": {"status": "Mandatory",         "strictness": "High",   "details": "Cybersecurity Management Act mandates risk assessments and incident reporting for agencies."},
            "Privacy & Data Protection":  {"status": "Comprehensive Law", "strictness": "Medium", "details": "PDPA administered by PDPO. Amendment to align with GDPR standards underway."},
            "Platform Regulations":       {"status": "Partial",           "strictness": "Low",    "details": "Digital Intermediary Services Act proposed. Currently light touch."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "FSC regulates digital banking and payment services. Open banking initiative."},
            "Trade Facilitation":         {"status": "Advanced",          "strictness": "Low",    "details": "Customs Single Window operational. Paperless processes advanced."},
        }
    },
    {
        "country": "Cambodia", "organization": "MPTC",
        "summary": "Cambodia is building its digital trade framework. E-Commerce Law passed in 2019. No comprehensive data protection law yet. RCEP and ASEAN membership provide trade facilitation benefits.",
        "openness_score": 4.0,
        "key_laws": ["E-Commerce Law 2019", "Telecommunications Law", "ICT Law (draft)"],
        "notable_features": ["RCEP member", "Developing data protection law", "ASEAN Single Window member"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No localization requirements currently in place."},
            "Cross-Border Data Flows":    {"status": "Limited Rules",     "strictness": "Medium", "details": "No comprehensive rules. Draft ICT Law expected to introduce provisions."},
            "E-Commerce Rules":           {"status": "Basic",             "strictness": "Medium", "details": "E-Commerce Law 2019 covers electronic contracts and online consumer protection."},
            "Digital Signatures":         {"status": "Partial",           "strictness": "High",   "details": "Limited recognition. Draft laws aim to strengthen e-signature framework."},
            "Consumer Protection":        {"status": "Basic",             "strictness": "Medium", "details": "E-Commerce Law has consumer protection provisions. Enforcement limited."},
            "Customs & Tariffs":          {"status": "High",              "strictness": "High",   "details": "Average tariff ~15%. ATIGA provides ASEAN preferences."},
            "Intellectual Property":      {"status": "Moderate",          "strictness": "Medium", "details": "Law on Marks and Copyright in place. Enforcement improving."},
            "Cybersecurity Requirements": {"status": "Voluntary",         "strictness": "Low",    "details": "National Cybersecurity Committee formed. Mandatory rules pending."},
            "Privacy & Data Protection":  {"status": "None",              "strictness": "High",   "details": "No comprehensive data protection law. Draft being developed."},
            "Platform Regulations":       {"status": "None",              "strictness": "Low",    "details": "No specific platform regulation yet."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "NBC regulates e-payment and fintech. Bakong digital payment system launched."},
            "Trade Facilitation":         {"status": "Basic",             "strictness": "Low",    "details": "Cambodia NSW connected to ASEAN Single Window."},
        }
    },
    {
        "country": "Lao PDR", "organization": "MICT",
        "summary": "Lao PDR has a basic digital framework under development. LDC status provides trade benefits. Limited regulatory capacity but RCEP and ASEAN membership help facilitate regional trade.",
        "openness_score": 3.5,
        "key_laws": ["Law on Electronic Data 2017", "Telecommunications Law", "E-Commerce Law (draft)"],
        "notable_features": ["LDC — preferential trade access", "RCEP & ASEAN member", "Developing digital laws"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No localization requirements."},
            "Cross-Border Data Flows":    {"status": "Limited Rules",     "strictness": "Medium", "details": "No comprehensive framework. Draft e-commerce law expected."},
            "E-Commerce Rules":           {"status": "Basic",             "strictness": "Medium", "details": "Law on Electronic Data covers basic e-commerce. Comprehensive law pending."},
            "Digital Signatures":         {"status": "Partial",           "strictness": "High",   "details": "Limited legal recognition. Implementation capacity limited."},
            "Consumer Protection":        {"status": "Basic",             "strictness": "High",   "details": "Basic consumer protection in place. Online-specific rules absent."},
            "Customs & Tariffs":          {"status": "High",              "strictness": "High",   "details": "Average tariff ~15%. ATIGA provides ASEAN preferences."},
            "Intellectual Property":      {"status": "Basic",             "strictness": "High",   "details": "IP Law in place but limited digital scope and enforcement."},
            "Cybersecurity Requirements": {"status": "None",              "strictness": "High",   "details": "No formal cybersecurity law. Basic government directives only."},
            "Privacy & Data Protection":  {"status": "None",              "strictness": "High",   "details": "No data protection law. Plans to develop one under ASEAN framework."},
            "Platform Regulations":       {"status": "None",              "strictness": "Low",    "details": "No platform-specific regulation."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "BOL regulates payments. Mobile money growing rapidly."},
            "Trade Facilitation":         {"status": "Basic",             "strictness": "Low",    "details": "Lao PDR NSW under development. ASEAN Single Window connected."},
        }
    },
    {
        "country": "Brunei", "organization": "iGovTT / AITI",
        "summary": "Brunei has zero digital tariffs and is a CPTPP and RCEP member. E-commerce framework is in place. Data protection law limited but regional agreement commitments provide some baseline.",
        "openness_score": 6.0,
        "key_laws": ["E-Commerce Order 2000", "Computer Misuse Act", "BDCB Guidelines"],
        "notable_features": ["Zero digital tariffs", "CPTPP & RCEP member", "ASEAN Single Window member"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No data localization requirement."},
            "Cross-Border Data Flows":    {"status": "Open",              "strictness": "Low",    "details": "No restrictions on cross-border flows. CPTPP provisions apply."},
            "E-Commerce Rules":           {"status": "Basic",             "strictness": "Low",    "details": "E-Commerce Order 2000 covers electronic contracts and signatures."},
            "Digital Signatures":         {"status": "Legally Recognized","strictness": "Low",    "details": "E-Commerce Order 2000 gives e-signatures legal recognition."},
            "Consumer Protection":        {"status": "Basic",             "strictness": "Low",    "details": "Consumer Protection Order covers online trade."},
            "Customs & Tariffs":          {"status": "Zero",              "strictness": "Low",    "details": "Zero tariffs across the board. Free port status."},
            "Intellectual Property":      {"status": "Moderate",          "strictness": "Medium", "details": "Copyright Order covers digital works. CPTPP aligned provisions."},
            "Cybersecurity Requirements": {"status": "Mandatory",         "strictness": "Medium", "details": "CIRT operates. CII rules apply to certain sectors."},
            "Privacy & Data Protection":  {"status": "Partial",           "strictness": "Medium", "details": "No comprehensive data protection law. BDCB issues guidelines."},
            "Platform Regulations":       {"status": "None",              "strictness": "Low",    "details": "No platform-specific regulations."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "AMBD regulates digital financial services."},
            "Trade Facilitation":         {"status": "Moderate",          "strictness": "Low",    "details": "Brunei NSW operational. ASEAN Single Window connected."},
        }
    },
    {
        "country": "Bangladesh", "organization": "BCC",
        "summary": "Bangladesh is developing its digital trade framework. LDC status provides preferential market access. No comprehensive data protection law. Growing RMG and ICT export sectors driving digital trade interest.",
        "openness_score": 3.5,
        "key_laws": ["Digital Security Act 2018", "ICT Act 2006", "Copyright Act 2000"],
        "notable_features": ["LDC — duty-free market access", "Developing digital laws", "Growing ICT exports"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No localization requirements currently."},
            "Cross-Border Data Flows":    {"status": "Limited Rules",     "strictness": "Medium", "details": "No comprehensive framework. Digital Security Act has some provisions."},
            "E-Commerce Rules":           {"status": "Basic",             "strictness": "Medium", "details": "No dedicated e-commerce law. ICT Act and contract law apply."},
            "Digital Signatures":         {"status": "Not Recognized",    "strictness": "High",   "details": "No formal e-signature law. Paper-based processes still required for most transactions."},
            "Consumer Protection":        {"status": "Basic",             "strictness": "High",   "details": "Consumer Rights Protection Act does not specifically cover online commerce."},
            "Customs & Tariffs":          {"status": "High",              "strictness": "High",   "details": "Average tariff ~20% on digital goods. LDC exemptions from partners partially offset this."},
            "Intellectual Property":      {"status": "Basic",             "strictness": "High",   "details": "Copyright Act covers digital works but enforcement is very limited."},
            "Cybersecurity Requirements": {"status": "Voluntary",         "strictness": "High",   "details": "BGD e-GOV CIRT provides guidance. No mandatory private sector rules."},
            "Privacy & Data Protection":  {"status": "None",              "strictness": "High",   "details": "No comprehensive data protection law. Draft PDPA under discussion."},
            "Platform Regulations":       {"status": "None",              "strictness": "Low",    "details": "Digital Security Act has broad content provisions affecting platforms."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "Bangladesh Bank regulates mobile financial services. bKash and Nagad major players."},
            "Trade Facilitation":         {"status": "Basic",             "strictness": "Medium", "details": "Bangladesh Single Window under development. Manual processes still common."},
        }
    },
    {
        "country": "Sri Lanka", "organization": "TRCSL",
        "summary": "Sri Lanka is building its data protection framework. Electronic Transactions Act exists. Moderate tariff environment. Strategic Indian Ocean location makes digital trade infrastructure increasingly important.",
        "openness_score": 4.0,
        "key_laws": ["Electronic Transactions Act 2006", "Computer Crimes Act 2007", "Payment Devices Frauds Act"],
        "notable_features": ["Moderate tariff rates", "Data protection law pending", "Strategic Indian Ocean location"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No localization requirements."},
            "Cross-Border Data Flows":    {"status": "Limited Rules",     "strictness": "Medium", "details": "No comprehensive framework. Pending data protection law will address this."},
            "E-Commerce Rules":           {"status": "Basic",             "strictness": "Medium", "details": "Electronic Transactions Act covers basic e-commerce. Amendment underway."},
            "Digital Signatures":         {"status": "Partial",           "strictness": "High",   "details": "Electronic Transactions Act covers e-signatures but practical recognition limited."},
            "Consumer Protection":        {"status": "Basic",             "strictness": "Medium", "details": "Consumer Affairs Authority Act extended to online. Enforcement limited."},
            "Customs & Tariffs":          {"status": "Moderate",          "strictness": "Medium", "details": "Average tariff ~15% on digital goods."},
            "Intellectual Property":      {"status": "Basic",             "strictness": "Medium", "details": "IP Act covers digital works. NIPO handles registration."},
            "Cybersecurity Requirements": {"status": "Voluntary",         "strictness": "Medium", "details": "Sri Lanka CERT coordinates. No mandatory private sector rules yet."},
            "Privacy & Data Protection":  {"status": "None",              "strictness": "High",   "details": "No data protection law. Personal Data Protection Bill drafted but not enacted."},
            "Platform Regulations":       {"status": "None",              "strictness": "Low",    "details": "No specific platform regulation."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "CBSL regulates e-money and payment systems. LankaPay national switch."},
            "Trade Facilitation":         {"status": "Basic",             "strictness": "Medium", "details": "Sri Lanka Customs Single Window under development."},
        }
    },
    {
        "country": "Papua New Guinea", "organization": "NICTA",
        "summary": "Papua New Guinea has limited digital trade infrastructure. Regulatory framework is basic. No comprehensive data protection law. Pacific regional cooperation provides some trade facilitation benefits.",
        "openness_score": 3.5,
        "key_laws": ["Electronic Transactions Act (draft)", "ICT Act 2009", "Copyright Act 2000"],
        "notable_features": ["Developing digital framework", "Pacific regional cooperation", "Limited digital infrastructure"],
        "topics": {
            "Data Localization":          {"status": "Not Required",      "strictness": "Low",    "details": "No localization requirements."},
            "Cross-Border Data Flows":    {"status": "No Rules Yet",      "strictness": "High",   "details": "No framework governing cross-border data flows."},
            "E-Commerce Rules":           {"status": "None",              "strictness": "High",   "details": "Electronic Transactions Act drafted but not enacted. No e-commerce law in force."},
            "Digital Signatures":         {"status": "Not Recognized",    "strictness": "High",   "details": "No legal framework for digital signatures."},
            "Consumer Protection":        {"status": "Basic",             "strictness": "High",   "details": "Consumer Protection Act does not cover online commerce specifically."},
            "Customs & Tariffs":          {"status": "Moderate",          "strictness": "Medium", "details": "Average tariff ~15%. Pacific trade agreements provide some preferences."},
            "Intellectual Property":      {"status": "Basic",             "strictness": "High",   "details": "Copyright Act exists but digital coverage and enforcement very limited."},
            "Cybersecurity Requirements": {"status": "None",              "strictness": "High",   "details": "No cybersecurity law or formal requirements."},
            "Privacy & Data Protection":  {"status": "None",              "strictness": "High",   "details": "No data protection law."},
            "Platform Regulations":       {"status": "None",              "strictness": "Low",    "details": "No platform regulation."},
            "Financial Digital Services": {"status": "Regulated",         "strictness": "Medium", "details": "BPNG regulates mobile money. BSP and Digicel are major mobile money providers."},
            "Trade Facilitation":         {"status": "Basic",             "strictness": "High",   "details": "Manual customs processes still dominant. Single Window planned."},
        }
    },
]


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(conn):
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL, organization TEXT,
            summary TEXT, openness_score REAL,
            notable_features TEXT, key_laws TEXT, analyzed_at TEXT,
            UNIQUE(country, organization)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS topic_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE,
            country TEXT, topic TEXT, status TEXT, strictness TEXT, details TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS key_laws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE,
            country TEXT, law_name TEXT
        )
    """)
    conn.commit()


def seed():
    print("\n" + "=" * 55)
    print("  SEED — Loading built-in sample data")
    print("=" * 55 + "\n")

    os.makedirs(DATA_FOLDER, exist_ok=True)
    conn = connect()
    create_tables(conn)
    c = conn.cursor()

    for rec in SAMPLE_DATA:
        country = rec["country"]

        c.execute("""
            INSERT OR REPLACE INTO countries
                (country, organization, summary, openness_score, notable_features, key_laws, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            country, rec["organization"], rec["summary"],
            rec["openness_score"],
            json.dumps(rec.get("notable_features", [])),
            json.dumps(rec.get("key_laws", [])),
            datetime.now().isoformat(),
        ))
        conn.commit()
        country_id = c.lastrowid

        for topic, data in rec["topics"].items():
            c.execute("""
                INSERT INTO topic_scores (country_id, country, topic, status, strictness, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (country_id, country, topic, data["status"], data["strictness"], data["details"]))

        for law in rec.get("key_laws", []):
            c.execute(
                "INSERT INTO key_laws (country_id, country, law_name) VALUES (?, ?, ?)",
                (country_id, country, law)
            )

        conn.commit()
        print(f"  + {country} ({rec['openness_score']}/10)")

    conn.close()
    print(f"\n  {len(SAMPLE_DATA)} economies loaded into {DB_FILE}")
    print(f"  Next step: python backend/server.py\n")


if __name__ == "__main__":
    seed()
