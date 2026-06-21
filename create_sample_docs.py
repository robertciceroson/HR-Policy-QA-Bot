"""
Generates a sample HR Policy PDF for testing the RAG bot.
Run: python create_sample_docs.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT

def create_hr_policy_pdf(output_path="sample_docs/HR_Policy_Handbook.pdf"):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16, spaceAfter=12)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13, spaceAfter=8)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=11,
                          leading=16, spaceAfter=8)

    content = []

    def heading(text, style=h1):
        content.append(Paragraph(text, style))
        content.append(Spacer(1, 0.1 * inch))

    def para(text):
        content.append(Paragraph(text, body))

    def space():
        content.append(Spacer(1, 0.2 * inch))

    # Cover
    heading("Acme Corp Employee Handbook", h1)
    para("Effective Date: January 1, 2026 | Version 3.2")
    para("This handbook outlines company policies for all full-time and part-time employees. "
         "Contact HR at hr@acmecorp.com with any questions.")
    space()

    # PTO
    heading("Section 1 — Paid Time Off (PTO)", h2)
    para("Acme Corp provides a flexible PTO policy that combines vacation, personal days, and "
         "floating holidays into a single PTO bank.")
    para("<b>PTO Accrual Schedule (Full-Time Employees):</b>")
    para("• Years 0–1: 10 days (80 hours) per year, accrued at 0.833 days per month")
    para("• Years 2–4: 15 days (120 hours) per year, accrued at 1.25 days per month")
    para("• Years 5–9: 20 days (160 hours) per year, accrued at 1.67 days per month")
    para("• Years 10+: 25 days (200 hours) per year, accrued at 2.08 days per month")
    para("<b>Eligibility:</b> PTO accrual begins on the employee's first day of employment. "
         "New employees may use accrued PTO after completing 90 days of employment (the probationary period).")
    para("<b>Carry-Over Policy:</b> Employees may carry over a maximum of 5 unused PTO days "
         "(40 hours) into the next calendar year. Any unused PTO above 5 days will be forfeited "
         "on December 31st each year. Carried-over PTO must be used by March 31st of the following year.")
    para("<b>PTO Payout:</b> Upon separation, employees will be paid out for all accrued, unused PTO "
         "up to a maximum of 10 days.")
    space()

    # Sick Leave
    heading("Section 2 — Sick Leave", h2)
    para("Sick leave is provided separately from the PTO bank to ensure employees can address "
         "health needs without depleting vacation time.")
    para("<b>Sick Leave Accrual:</b> All full-time employees accrue 1 sick day (8 hours) per month, "
         "up to a maximum of 12 sick days (96 hours) per calendar year.")
    para("<b>Part-Time Employees:</b> Part-time employees working 20+ hours per week accrue sick "
         "leave on a prorated basis — 0.5 days per month, up to 6 days per year.")
    para("<b>Eligibility:</b> Sick leave is available for use immediately upon hire with no waiting period.")
    para("<b>Carry-Over:</b> Up to 5 unused sick days may be carried over to the following year. "
         "Sick leave does not accrue beyond 17 days at any time (12 current year + 5 carried over).")
    para("<b>Sick leave may be used for:</b>")
    para("• Personal illness or injury")
    para("• Medical, dental, or mental health appointments")
    para("• Caring for an immediate family member who is ill")
    para("• Pregnancy-related conditions")
    para("<b>Sick Leave Payout:</b> Unused sick leave is not paid out upon separation from the company.")
    space()

    # Vacation
    heading("Section 3 — Vacation Policy", h2)
    para("For employees hired prior to January 1, 2024, vacation days were tracked separately "
         "from the PTO bank under the legacy vacation policy below. Employees hired on or after "
         "January 1, 2024 are covered under the unified PTO policy in Section 1.")
    para("<b>Legacy Vacation Accrual (Pre-2024 Hires):</b>")
    para("• Years 0–2: 10 vacation days per year")
    para("• Years 3–6: 15 vacation days per year")
    para("• Years 7+: 20 vacation days per year")
    para("<b>Vacation Scheduling:</b> Vacation requests must be submitted at least 2 weeks in advance "
         "and are subject to manager approval. No more than 2 employees in the same department may "
         "take vacation simultaneously without VP approval.")
    space()

    # 401k
    heading("Section 4 — 401(k) Retirement Plan", h2)
    para("Acme Corp offers a 401(k) retirement savings plan administered through Fidelity Investments. "
         "Employees are encouraged to take full advantage of the company match.")
    para("<b>Eligibility:</b> All full-time employees are eligible to enroll in the 401(k) plan "
         "after completing 90 days of continuous employment. Enrollment windows open on the first "
         "day of each calendar quarter (January 1, April 1, July 1, October 1).")
    para("<b>Company Match:</b> Acme Corp matches 100% of employee contributions up to 4% of the "
         "employee's gross annual salary. Contributions above 4% are not matched.")
    para("<b>Example:</b> If you earn $60,000 and contribute 4% ($2,400), Acme Corp contributes "
         "an additional $2,400 — for a total annual retirement contribution of $4,800.")
    para("<b>Vesting Schedule:</b> The company match is subject to a 3-year graded vesting schedule:")
    para("• After Year 1: 0% vested in company match")
    para("• After Year 2: 33% vested in company match")
    para("• After Year 3: 67% vested in company match")
    para("• After Year 4: 100% vested in company match")
    para("Employee contributions are always 100% vested immediately.")
    para("<b>Contribution Limits:</b> For 2026, the IRS contribution limit is $23,500 for employees "
         "under age 50. Employees age 50 and older may contribute an additional $7,500 "
         "catch-up contribution for a total of $31,000.")
    para("<b>Investment Options:</b> Employees may choose from 20+ Fidelity index funds and target-date "
         "funds. Contact benefits@acmecorp.com or visit netbenefits.fidelity.com to manage your account.")
    space()

    # Health Benefits
    heading("Section 5 — Health & Dental Benefits", h2)
    para("<b>Eligibility:</b> Full-time employees (30+ hours/week) are eligible for health and dental "
         "benefits on the first day of the month following their 30-day waiting period.")
    para("<b>Health Insurance:</b> Acme Corp covers 80% of the employee-only premium and 60% of "
         "dependent premiums for the company's standard PPO plan.")
    para("<b>Dental Insurance:</b> Acme Corp covers 100% of the employee-only dental premium. "
         "Dependent dental coverage is available at the employee's expense.")
    space()

    # Holidays
    heading("Section 6 — Company Holidays", h2)
    para("Acme Corp observes 11 paid company holidays per year:")
    para("New Year's Day, Martin Luther King Jr. Day, Presidents' Day, Memorial Day, "
         "Juneteenth, Independence Day, Labor Day, Columbus Day, Veterans Day, "
         "Thanksgiving Day, Christmas Day.")
    para("When a holiday falls on a Saturday, it is observed on the preceding Friday. "
         "When it falls on a Sunday, it is observed on the following Monday.")
    space()

    # Contact
    heading("Section 7 — HR Contact Information", h2)
    para("For questions about any policy in this handbook, contact the HR team:")
    para("• Email: hr@acmecorp.com")
    para("• Phone: (800) 555-0100 ext. 2")
    para("• HR Portal: hr.acmecorp.com")
    para("• Office hours: Monday–Friday, 9:00 AM – 5:00 PM ET")

    doc.build(content)
    print(f"Created: {output_path}")

if __name__ == "__main__":
    create_hr_policy_pdf()
