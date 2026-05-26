"""
GovernAI Studio — Text Corpus Builder
Creates structured text corpus from key Indian governance documents.
Since PDFs aren't available, this builds the corpus directly from
authoritative text content for GraphRAG ingestion.

Usage: python scripts/build_corpus.py
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# ============================================================
# GOVERNANCE CORPUS — Key sections from Indian legal documents
# ============================================================

CORPUS_DOCUMENTS = [

# --- 1. DPDP Act 2023 ---
{
"title": "Digital Personal Data Protection Act 2023",
"type": "statute",
"year": 2023,
"sections": [
{"ref": "Section 2", "text": """
Section 2 - Definitions. (1) In this Act, unless the context otherwise requires:
(a) "Consent Manager" means a person registered with the Board who enables a Data Principal to give, manage, review, and withdraw her consent through an accessible, transparent, and interoperable platform.
(b) "Data Fiduciary" means any person who alone or in conjunction with other persons determines the purpose and means of processing of personal data.
(c) "Data Principal" means the individual to whom the personal data relates and where such individual is a child, includes the parents or lawful guardian of such child, and in relation to a person with disability, includes her lawful guardian.
(d) "Data Processor" means any person who processes personal data on behalf of a Data Fiduciary.
(e) "personal data" means any data about an individual who is identifiable by or in relation to such data.
"""},
{"ref": "Section 4", "text": """
Section 4 - Consent. Personal data may be processed only in accordance with the provisions of this Act and for a lawful purpose. For the purposes of this section, the consent given by the Data Principal shall be free, specific, informed, unconditional and unambiguous with a clear affirmative action, and shall signify an agreement to the processing of her personal data for the specified purpose and be limited to such personal data as is necessary for such specified purpose.
"""},
{"ref": "Section 5", "text": """
Section 5 - Notice. Every Data Fiduciary shall, before or at the time of collection of personal data, give to the Data Principal an itemised notice in clear and plain language containing a description of personal data to be collected and the purpose of processing of such personal data, and the manner in which she may exercise her rights under this Act, and the manner in which a complaint may be made to the Board.
"""},
{"ref": "Section 6", "text": """
Section 6 - Legitimate uses. A Data Fiduciary may process personal data of a Data Principal for certain legitimate uses including: (a) the State or any instrumentality of the State for any function under any law for the time being in force; (b) compliance with any judgment or order issued under any law; (c) medical emergency involving a threat to life; (d) safety measures during any disaster or breakdown of public order.
"""},
{"ref": "Section 8", "text": """
Section 8 - Obligations of Data Fiduciary. (1) A Data Fiduciary shall make reasonable efforts to ensure the accuracy and completeness of personal data. (2) A Data Fiduciary shall build reasonable security safeguards to prevent personal data breach. (3) In the event of a personal data breach, the Data Fiduciary shall give the Board and each affected Data Principal, intimation of such breach in such form and manner as may be prescribed. (4) When the purpose for which personal data was collected is no longer being served and retention is not necessary for legal purposes, the Data Fiduciary shall erase such personal data.
"""},
{"ref": "Section 9", "text": """
Section 9 - Significant Data Fiduciary. The Central Government may, having regard to the volume and sensitivity of personal data processed, risk to the rights of Data Principal, and potential impact on the sovereignty and integrity of India, notify any Data Fiduciary or class of Data Fiduciaries as Significant Data Fiduciary. A Significant Data Fiduciary shall appoint a Data Protection Officer and an independent data auditor.
"""},
{"ref": "Section 16", "text": """
Section 16 - Transfer of personal data outside India. The Central Government may, by notification, restrict the transfer of personal data by a Data Fiduciary for processing to such country or territory outside India as may be so notified. The transfer shall be subject to such terms and conditions as the Central Government may prescribe.
"""},
{"ref": "Section 18", "text": """
Section 18 - Data Protection Board of India. The Central Government shall establish a Board to be known as the Data Protection Board of India for the purpose of determining non-compliance with the provisions of this Act, imposing penalties, and directing remedial measures.
"""},
]},

# --- 2. IT Act 2000 ---
{
"title": "Information Technology Act 2000",
"type": "statute",
"year": 2000,
"sections": [
{"ref": "Section 43A", "text": """
Section 43A - Compensation for failure to protect data. Where a body corporate, possessing, dealing or handling any sensitive personal data or information in a computer resource which it owns, controls or operates, is negligent in implementing and maintaining reasonable security practices and procedures and thereby causes wrongful loss or wrongful gain to any person, such body corporate shall be liable to pay damages by way of compensation to the person so affected.
"""},
{"ref": "Section 66", "text": """
Section 66 - Computer Related Offences. If any person, dishonestly or fraudulently, does any act referred to in section 43, he shall be punishable with imprisonment for a term which may extend to three years or with fine which may extend to five lakh rupees or with both.
"""},
{"ref": "Section 69", "text": """
Section 69 - Power to issue directions for interception or monitoring or decryption of any information through any computer resource. Where the Central Government or a State Government is satisfied that it is necessary or expedient so to do, in the interest of the sovereignty or integrity of India, defence of India, security of the State, friendly relations with foreign States or public order, it may direct any agency of the appropriate Government to intercept, monitor or decrypt any information generated, transmitted, received or stored in any computer resource.
"""},
{"ref": "Section 70B", "text": """
Section 70B - Indian Computer Emergency Response Team (CERT-In). (1) The Central Government shall, by notification in the Official Gazette, appoint an agency of the Government to be called the Indian Computer Emergency Response Team. (2) The Indian Computer Emergency Response Team shall serve as the national agency for performing the following functions: (a) collection, analysis and dissemination of information on cyber incidents; (b) forecast and alerts of cyber security incidents; (c) emergency measures for handling cyber security incidents; (d) coordination of cyber incidents response activities; (e) issue guidelines, advisories, vulnerability notes and white papers relating to information security practices.
"""},
{"ref": "Section 79", "text": """
Section 79 - Exemption from liability of intermediary in certain cases. An intermediary shall not be liable for any third party information, data, or communication link made available or hosted by him if he merely provides access to a communication system and does not initiate the transmission, select the receiver, or modify the information. However, this shall not apply if the intermediary has conspired or abetted or aided or induced the commission of the unlawful act, or upon receiving actual knowledge fails to expeditiously remove or disable access.
"""},
]},

# --- 3. GFR 2017 ---
{
"title": "General Financial Rules 2017",
"type": "statute",
"year": 2017,
"sections": [
{"ref": "Rule 144", "text": """
Rule 144 - Fundamental principles of public buying. Every authority delegated with the financial powers of procuring goods in the public interest shall have the responsibility and accountability to bring efficiency, economy and transparency in matters relating to public procurement. The cardinal principle is that every public buyer should get best value for money. This means the total cost of ownership over the useful life, not merely the initial price.
"""},
{"ref": "Rule 149", "text": """
Rule 149 - Modes of procurement. Procurement of goods up to Rs.25,000 may be made through any convenient mode. Procurement above Rs.25,000 and up to Rs.2,50,000 shall be done by Purchase Committee. Direct procurement may be done from GeM (Government e-Marketplace). For procurement above Rs.25 lakh, competitive bidding is mandatory through open tender on Central Public Procurement Portal (CPPP).
"""},
{"ref": "Rule 154", "text": """
Rule 154 - Mandatory procurement from GeM. All ministries and departments shall procure Goods and Services available on GeM. The procuring authorities shall mandatorily procure from GeM portal the Goods or Services that are available. The Procurement of Goods and Services by Ministries or Departments shall be mandatory for Goods or Services available on GeM.
"""},
{"ref": "Rule 173", "text": """
Rule 173 - Outsourcing of services. A ministry or department may outsource certain services in the interest of economy and efficiency. Such outsourcing shall be through open competitive bidding. The terms of outsourcing agreement should clearly define service level standards, penalties for non-performance, exit clause, and data security obligations.
"""},
{"ref": "Rule 230", "text": """
Rule 230 - Single tender enquiry. Procurement from a single source may be resorted to in the following circumstances: (a) it is in the knowledge of the user department that only a particular firm is the manufacturer of the required goods; (b) in a case of emergency; (c) for standardization of machinery or spare parts. Reasons for single source procurement must be recorded in writing and approved by the competent authority.
"""},
]},

# --- 4. India AI Governance Guidelines 2025 ---
{
"title": "India AI Governance Guidelines 2025 - Seven Sutras",
"type": "guideline",
"year": 2025,
"sections": [
{"ref": "Sutra 1 - Trust is the Foundation", "text": """
Sutra 1: Trust is the Foundation. AI systems deployed in governance must earn and maintain public trust through transparency, explainability, and accountability. Every AI system should provide clear documentation of its purpose, data sources, limitations, and decision-making processes. Citizens must be informed when AI is being used in decisions that affect them. Trust is not assumed — it is built through consistent demonstration of reliability, fairness, and respect for rights.
"""},
{"ref": "Sutra 2 - Guardrails, Not Gatekeepers", "text": """
Sutra 2: Guardrails, Not Gatekeepers. AI governance should enable innovation while ensuring safety. The framework favors proportionate, risk-based regulation over blanket restrictions. High-risk applications (healthcare, criminal justice, welfare distribution) require stricter oversight. Low-risk applications should be encouraged with lighter-touch governance. The goal is to create a supportive ecosystem for responsible AI, not to block progress.
"""},
{"ref": "Sutra 3 - Innovation Over Restraint", "text": """
Sutra 3: Innovation Over Restraint. India's approach to AI governance prioritizes enabling responsible innovation. Government should create sandbox environments for testing AI applications. Procurement processes should not create barriers to innovative solutions. The India AI Mission aims to build indigenous AI capacity through research, skilling, and compute infrastructure.
"""},
{"ref": "Sutra 4 - Responsible by Design", "text": """
Sutra 4: Responsible by Design. AI systems must incorporate ethical considerations from the design phase, not as an afterthought. This includes privacy-by-design principles from the DPDP Act, fairness testing before deployment, bias audits for systems affecting vulnerable populations, and environmental impact assessment for large-scale AI deployments.
"""},
{"ref": "Sutra 5 - Fairness and Equity", "text": """
Sutra 5: Fairness and Equity. AI systems in governance must not discriminate. This is particularly critical in India's diverse context where AI training data may reflect historical biases related to caste, gender, religion, and economic status. Systems must be tested for disparate impact across protected categories. Special attention is required for AI used in welfare targeting, credit scoring, and public service delivery.
"""},
{"ref": "Sutra 6 - People First", "text": """
Sutra 6: People First. The ultimate purpose of AI in governance is to improve citizen outcomes, not to optimize for administrative convenience. AI should augment human decision-making, not replace it in consequential decisions. Citizens should have the right to human review of AI-assisted decisions that significantly affect them. No citizen should be denied a government service solely because an AI system flagged them.
"""},
{"ref": "Sutra 7 - Accountability", "text": """
Sutra 7: Accountability. Clear chains of responsibility must exist for AI-assisted decisions. The deploying institution, not the vendor, bears ultimate responsibility. Officers must understand the AI tools they deploy. Audit trails must be maintained for all AI-assisted decisions. There must be accessible redressal mechanisms for citizens affected by AI decisions.
"""},
]},

# --- 5. RTI Act 2005 ---
{
"title": "Right to Information Act 2005",
"type": "statute",
"year": 2005,
"sections": [
{"ref": "Section 3", "text": """
Section 3 - Right to information. Subject to the provisions of this Act, all citizens shall have the right to information.
"""},
{"ref": "Section 4", "text": """
Section 4 - Obligations of public authorities. Every public authority shall maintain all its records duly catalogued and indexed in a manner and form which facilitates the right to information under this Act. Every public authority shall publish within one hundred and twenty days: (a) the particulars of its organization, functions and duties; (b) the powers and duties of its officers; (c) the procedure followed in the decision making process, including channels of supervision and accountability; (d) the norms set by it for the discharge of its functions.
"""},
{"ref": "Section 6", "text": """
Section 6 - Request for obtaining information. A person who desires to obtain any information shall make a request in writing or through electronic means to the Central Public Information Officer or State Public Information Officer specifying the particulars of the information sought. The applicant shall not be required to give any reason for requesting the information.
"""},
{"ref": "Section 8", "text": """
Section 8 - Exemption from disclosure of information. There shall be no obligation to give any citizen information that would prejudicially affect the sovereignty and integrity of India, the security, strategic, scientific or economic interests of the State, or would cause a breach of privilege of Parliament or the State Legislature. Information available to a person in his fiduciary relationship shall also be exempt.
"""},
]},

# --- 6. Aadhaar Act 2016 ---
{
"title": "Aadhaar (Targeted Delivery of Financial and Other Subsidies, Benefits and Services) Act 2016",
"type": "statute",
"year": 2016,
"sections": [
{"ref": "Section 3", "text": """
Section 3 - Aadhaar number. Every resident shall be entitled to obtain an Aadhaar number by submitting his demographic information and biometric information by undergoing the process of enrolment. The Aadhaar number issued to an individual shall not be re-assigned to any other individual.
"""},
{"ref": "Section 7", "text": """
Section 7 - Proof of Aadhaar number for receipt of certain subsidies, benefits and services. The Central Government or a State Government may require an individual to furnish proof of possession of Aadhaar number for the purpose of establishing the identity of the individual as a condition for receipt of a subsidy, benefit or service. Provided that if an Aadhaar number is not assigned, the individual shall be offered alternate and viable means of identification for delivery of the subsidy, benefit or service.
"""},
{"ref": "Section 28", "text": """
Section 28 - Security and confidentiality of information. The Authority shall ensure the security of identity information and authentication records of individuals. The identity information collected at the time of enrolment shall be stored in the Central Identities Data Repository. No identity information available with a requesting entity shall be used for any purpose other than that specified to the individual.
"""},
{"ref": "Section 29", "text": """
Section 29 - Restriction on sharing information. No core biometric information, collected or created under this Act, shall be shared with anyone for any reason whatsoever. No identity information available with a requesting entity shall be published, displayed or posted publicly, except for the purposes as may be specified by regulations.
"""},
]},

# --- 7. NITI Aayog Responsible AI 2021 ---
{
"title": "NITI Aayog Responsible AI Principles 2021",
"type": "framework",
"year": 2021,
"sections": [
{"ref": "Principle 1 - Safety and Reliability", "text": """
Principle 1: Safety and Reliability. AI systems should be safe and reliable throughout their lifecycle. Systems should perform consistently under a wide range of conditions and should not pose unreasonable safety risks. AI systems deployed in critical infrastructure should have fallback mechanisms and human oversight provisions.
"""},
{"ref": "Principle 2 - Equality", "text": """
Principle 2: Equality. AI systems should be designed to minimize bias and promote equal treatment. In the Indian context, this requires specific attention to caste, gender, religious, linguistic, and economic biases that may be embedded in training data. AI systems used for welfare targeting should be audited for disparate impact.
"""},
{"ref": "Principle 3 - Inclusivity", "text": """
Principle 3: Inclusivity and Non-Discrimination. AI development should be inclusive, ensuring that benefits of AI are shared broadly. Special measures should be taken to ensure that AI does not further marginalize disadvantaged communities. AI interfaces should accommodate India's linguistic diversity and varying levels of digital literacy.
"""},
{"ref": "Principle 4 - Privacy and Security", "text": """
Principle 4: Privacy and Security. AI systems should respect privacy and ensure the security of personal data. Data minimization principles should be followed. AI development should align with the Digital Personal Data Protection Act. Organizations deploying AI should conduct Privacy Impact Assessments.
"""},
{"ref": "Principle 5 - Transparency", "text": """
Principle 5: Transparency and Explainability. AI systems should be transparent and explainable to the extent possible. For high-stakes decisions, explanations should be provided in language understandable to the affected individual. The rationale behind AI-assisted government decisions should be auditable and reconstructable.
"""},
{"ref": "Principle 6 - Accountability", "text": """
Principle 6: Accountability. Clear governance structures should exist for AI deployment. The deploying organization bears primary accountability. Officers using AI tools should be trained in understanding their limitations. Redressal mechanisms should be accessible and timely.
"""},
]},

# --- 8. CERT-In Rules ---
{
"title": "CERT-In Cyber Security Directions 2022",
"type": "guideline",
"year": 2022,
"sections": [
{"ref": "Direction 1", "text": """
All service providers, intermediaries, data centres, body corporate and Government organisations shall mandatorily report cyber incidents to CERT-In within six hours of noticing such incidents or being brought to notice about such incidents.
"""},
{"ref": "Direction 2", "text": """
Types of cyber incidents that must be reported include: targeted scanning/probing of critical networks, compromise of critical systems, unauthorized access of IT systems, defacement of website, malicious code attacks, attacks on servers, identity theft, spoofing and phishing attacks, denial of service attacks, data breach, data leak, attacks on critical infrastructure, attacks on IoT devices and associated systems.
"""},
{"ref": "Direction 3", "text": """
All service providers, intermediaries, data centres, body corporate and Government organisations shall maintain logs of all their ICT systems for a rolling period of 180 days. Such logs shall be maintained within the Indian jurisdiction. Logs shall be provided to CERT-In along with reporting of any incident or when ordered by CERT-In.
"""},
]},

# --- 9. Consumer Protection Act 2019 (AI relevant) ---
{
"title": "Consumer Protection Act 2019",
"type": "statute",
"year": 2019,
"sections": [
{"ref": "Section 2(7) - Deficiency", "text": """
Section 2(7) - "deficiency" means any fault, imperfection, shortcoming, or inadequacy in the quality, nature, and manner of performance which is required to be maintained by or under any law for the time being in force or has been undertaken to be performed by a person in pursuance of a contract or otherwise in relation to any service and includes any act of negligence or omission or commission by such person which causes loss or injury to the consumer.
"""},
{"ref": "Section 2(9) - E-commerce", "text": """
Section 2(9) - "electronic service provider" means a person who provides technologies or processes to enable a product seller to engage in advertising or selling goods or services to a consumer and includes any online marketplace or online auction site.
"""},
]},

# --- 10. Puttaswamy Judgment (Privacy) ---
{
"title": "Justice K.S. Puttaswamy v Union of India - Privacy Judgment 2017",
"type": "framework",
"year": 2017,
"sections": [
{"ref": "Proportionality Test", "text": """
The Supreme Court in Puttaswamy established a four-fold proportionality test for state intrusion on privacy: (1) Legality — the action must be sanctioned by law; (2) Legitimate aim — it must pursue a legitimate state aim; (3) Proportionality — the extent of interference must be proportionate to the need; (4) Procedural safeguards — there must be procedural guarantees against abuse.
"""},
{"ref": "Right to Privacy", "text": """
The right to privacy is a fundamental right under Article 21 of the Constitution. It includes informational privacy (the right to control dissemination of personal information), decisional privacy, and bodily integrity. Any state action that infringes on privacy must satisfy the test of proportionality. The right to privacy is not absolute and may be subject to reasonable restrictions.
"""},
{"ref": "Data Protection Principles", "text": """
The Court recognized that a robust data protection framework is essential for the right to privacy. Such a framework must include: fair and reasonable purpose limitation, collection limitation, data quality, openness and transparency, individual participation and accountability, and safeguards against unauthorized access or breach.
"""},
]},

# --- 11. Article 14 and 21 ---
{
"title": "Constitution of India - Fundamental Rights",
"type": "statute",
"year": 1950,
"sections": [
{"ref": "Article 14", "text": """
Article 14 - Equality before law. The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India. This principle of equality requires that equals be treated equally and unequals be treated differently. In the context of AI, this means algorithmic systems must not create arbitrary classifications or discriminatory outcomes.
"""},
{"ref": "Article 15", "text": """
Article 15 - Prohibition of discrimination on grounds of religion, race, caste, sex or place of birth. (1) The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex, place of birth or any of them. This is directly relevant to AI bias — if an algorithm produces disparate outcomes based on these protected characteristics, even through proxy variables, it may violate Article 15.
"""},
{"ref": "Article 19(1)(a)", "text": """
Article 19(1)(a) - Freedom of speech and expression. All citizens shall have the right to freedom of speech and expression. This right has implications for AI content moderation, deepfake regulation, and the use of AI for surveillance that may create chilling effects on free expression.
"""},
{"ref": "Article 21", "text": """
Article 21 - Protection of life and personal liberty. No person shall be deprived of his life or personal liberty except according to procedure established by law. The Supreme Court has interpreted this broadly to include the right to livelihood, right to dignity, right to privacy (Puttaswamy), and protection from arbitrary state action. AI systems that deny welfare benefits or services may implicate Article 21.
"""},
]},

# --- 12. GeM Procurement Guidelines ---
{
"title": "Government e-Marketplace (GeM) Guidelines",
"type": "guideline",
"year": 2024,
"sections": [
{"ref": "GeM 1 - Mandatory Usage", "text": """
All Central Government Ministries, Departments, and CPSEs shall procure goods and services available on GeM, through GeM. The procurement of goods and services not available on GeM shall follow GFR provisions for open competitive bidding.
"""},
{"ref": "GeM 2 - Transparency", "text": """
GeM ensures transparency in government procurement through: standardized product specifications, published price comparisons, e-bidding for large procurements, complete audit trail of all transactions, and rating system for sellers based on performance.
"""},
{"ref": "GeM 3 - AI Procurement", "text": """
For AI/ML solutions procurement through GeM, the buyer must specify: functional requirements, data handling requirements including compliance with DPDP Act, performance benchmarks, testing and acceptance criteria, source code access requirements, and exit/transition clauses.
"""},
]},
]


def build_chunks():
    """Convert corpus documents into formatted chunks for LightRAG."""
    chunks = []
    for doc in CORPUS_DOCUMENTS:
        for section in doc["sections"]:
            chunk = (
                f"[Document: {doc['title']}] "
                f"[Section: {section['ref']}] "
                f"[Type: {doc['type']}] "
                f"[Year: {doc['year']}]\n\n"
                f"{section['text'].strip()}"
            )
            chunks.append(chunk)
    return chunks


async def main():
    print("=" * 60)
    print("GovernAI Studio - Corpus Builder & Graph Ingestion")
    print("=" * 60)

    # Step 1: Build chunks
    print("\n[1/3] Building text corpus...")
    chunks = build_chunks()
    print(f"  Documents: {len(CORPUS_DOCUMENTS)}")
    print(f"  Total chunks: {len(chunks)}")
    total_chars = sum(len(c) for c in chunks)
    print(f"  Total characters: {total_chars:,}")

    # Save processed chunks for reference
    processed_dir = Path("corpus/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    with open(processed_dir / "all_chunks.txt", "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"=== CHUNK {i+1} ===\n{chunk}\n\n")
    print(f"  Saved to corpus/processed/all_chunks.txt")

    # Step 2: Ingest into LightRAG
    print("\n[2/3] Ingesting into LightRAG knowledge graph...")
    print("  Using Gemini for entity extraction (rate limited to 15 RPM)")

    from app.corpus.graph_builder import GovernAIGraphBuilder
    builder = GovernAIGraphBuilder(working_dir="./graph_data")
    await builder.ensure_initialized()
    print("  Storages initialized OK")

    batch_size = 5
    total = len(chunks)
    for i in range(0, total, batch_size):
        batch = chunks[i:i+batch_size]
        combined = "\n\n---\n\n".join(batch)
        try:
            await builder.rag.ainsert(combined)
            done = min(i + batch_size, total)
            print(f"  [{done}/{total}] chunks ingested")
        except Exception as e:
            print(f"  [WARN] Batch {i//batch_size + 1} error: {str(e)[:80]}")
            print("  Waiting 60s for rate limit cooldown...")
            await asyncio.sleep(60)
            try:
                await builder.rag.ainsert(combined)
                done = min(i + batch_size, total)
                print(f"  [{done}/{total}] chunks ingested (retry OK)")
            except Exception as e2:
                print(f"  [SKIP] Batch failed after retry: {str(e2)[:80]}")

        # Rate limit pause every 3 batches
        if (i // batch_size) % 3 == 2:
            print("  (rate limit pause 15s)")
            await asyncio.sleep(15)

    # Step 3: Verify
    print("\n[3/3] Verifying knowledge graph...")
    stats = builder.get_stats()
    print(f"  Status: {stats['status']}")
    print(f"  Entities: {stats.get('entities', 'N/A')}")
    print(f"  Relationships: {stats.get('relationships', 'N/A')}")

    print("\n" + "=" * 60)
    print("Corpus ingestion complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
