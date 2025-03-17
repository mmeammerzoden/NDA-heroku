from flask import Flask, request, render_template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fpdf import FPDF
import base64
from io import BytesIO
from PIL import Image
import os
import logging
import time

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

NDA_TEXT = """
Non-Disclosure Agreement
This Non-Disclosure Agreement (this "Agreement") is made as of April 3, 2024, between MME Houdstermaatschappij, a private company organized under the laws of the Netherlands, whose address is Wordragensestraat 36B, 5324 JM Ammerzoden, The Netherlands ("MME"), and {company_name}, a private company organized under the laws of the Netherlands, whose address is {full_address}, The Netherlands ("Recipient"). The following legal entities (and their respective affiliates) shall be deemed to be affiliates of MME: MME Ammerzoden B.V., Mycelium Materials Europe B.V., MME Horst B.V. and Kineco B.V.

The above named parties desire to have discussions regarding a business opportunity of mutual interest (the "Business Purpose"). In connection with such discussions and such relationship, the parties recognize that there is a need for MME to disclose to Recipient certain Confidential Information (as defined herein) to be used only for the Business Purpose and to protect such Confidential Information from unauthorized use and disclosure.

In consideration of the MME's disclosure of such Confidential Information, Recipient agrees as follows:

1. For purposes of this Agreement, "Confidential Information" means any information or materials disclosed by MME to the Recipient, whether disclosed before or after the date of this Agreement, that: (i) consists of non-public technical or business information or materials including but not limited to information relating to the disclosing party's product plans, designs, ideas, concepts, costs, prices, finances, marketing plans, business opportunities, personnel, trade secrets, research, development and know-how; (ii) if disclosed in writing, is marked "confidential" or "proprietary" at the time of such disclosure; (iii) if disclosed orally, is identified as "confidential" or "proprietary" at the time of such disclosure; or (iv) due to its nature or the circumstances of its disclosure, a person exercising reasonable business judgment would understand to be confidential or proprietary.

2. Recipient agrees: (i) to maintain MME's Confidential Information in strict confidence using at least the same degree of care as it uses to protect the confidentiality of its own confidential information, but no less than a reasonable degree of care; (ii) not to disclose such Confidential Information to any third parties; and (iii) not to use any such Confidential Information for any purpose except for the Business Purpose. Recipient may disclose the Confidential Information of MME to its employees and consultants who have a bona fide need to know such Confidential Information for the Business Purpose, but solely to the extent necessary to pursue the Business Purpose and for no other purpose; provided that each such employee and consultant first executes a written agreement (or is otherwise already bound by a written agreement) that contains use and nondisclosure restrictions at least as protective of MME's Confidential Information as those set forth in this Agreement. The provisions of this Section 2 will not restrict the Recipient from disclosing MME's Confidential Information to the extent required by any law or regulation; provided that the Recipient required to make such a disclosure promptly notifies MME of such required disclosure and cooperates with the other party to prevent or limit such disclosure. Recipient may comply with any court order or other legal requirement compelling disclosure of the other party's Confidential Information, but any Confidential Information so disclosed shall continue to be treated as Confidential Information for all purposes hereunder.

3. The Recipient's obligations in Section 2 will not apply to the extent any Confidential Information:
   (i) is now or hereafter becomes generally known or available to the public, through no act or omission on the part of Recipient;
   (ii) was known, without restriction as to use or disclosure, by Recipient prior to receiving such information from the disclosing party as evidenced by contemporaneous written records;
   (iii) is rightfully acquired by Recipient from a third party who has the right to disclose it and who provides it without restriction as to use or disclosure; or
   (iv) is independently developed by Recipient without access to any Confidential Information of the disclosing party as evidenced by contemporaneous written records.

4. Upon the completion or abandonment of the Business Purpose, and in any event upon the MME's request, the Recipient will promptly return to the disclosing party all tangible items and embodiments containing or consisting of the disclosing party's Confidential Information and all copies thereof (including electronic copies) and any notes, analyses, compilations, studies, interpretations, memoranda or other documents (regardless of the form thereof) prepared by or on behalf of the Recipient that contain or that are based upon MME's Confidential Information, and will provide MME with a written officer's certificate certifying the receiving party's compliance with the foregoing obligation. Notwithstanding the foregoing, Recipient may retain an archival copy of the disclosing party's Confidential Information for compliance and legal purposes.

5. All Confidential Information remains the sole and exclusive property of MME. Each party acknowledges and agrees that nothing in this Agreement will be construed as granting any rights to the Recipient, by license or otherwise, in or to any Confidential Information or any patent, copyright or other intellectual property or proprietary rights of the disclosing party, except as specified in this Agreement.

6. ALL CONFIDENTIAL INFORMATION IS PROVIDED BY MME "AS IS." MME makes no warranties, express, implied or otherwise, regarding its accuracy, fitness for use, completeness or performance, except that MME represents that it has the authority to disclose the Confidential Information that it discloses to the Recipient.

7. Each party acknowledges that the unauthorized use or disclosure of MME's Confidential Information would cause MME to incur irreparable harm and significant damages, the degree of which may be difficult to ascertain. Accordingly, each party agrees that MME will have the right to obtain immediate equitable relief to enjoin any unauthorized use or disclosure of its Confidential Information, in addition to any other rights and remedies that it may have at law or otherwise.

8. This Agreement will be construed, interpreted, and applied in accordance with the internal laws of the Netherlands (excluding its body of law controlling conflicts of law). This Agreement is the complete and exclusive statement regarding the subject matter of this Agreement and supersedes all prior agreements, understandings and communications, oral or written, between the parties regarding the subject matter of this Agreement. Recipient may not assign this Agreement, in whole or in part, without the MME's prior written consent, and any attempted assignment without such consent will be void, provided, however, that no consent shall be required for any assignment to a third party in connection with any merger, acquisition, or sale of all or substantially all of the assets of the business of either party, provided that the third party agrees in writing to be bound by the terms and conditions of this Agreement. Any assignment or transfer of this Agreement made in contravention of the terms hereof shall be null and void. Subject to the foregoing, this Agreement shall be binding on and inure to the benefit of the parties' respective successors and permitted assigns.

9. This Agreement will commence on the date first set forth above and will remain in effect for five (5) years from the date of the last disclosure of Confidential Information by MME, at which time it will terminate; provided, that as to any Confidential Information that the MME maintains as a trade secret, this Agreement will remain in effect for as long such Confidential Information remains a trade secret under applicable law.

10. This Agreement may be executed in multiple counterparts, each of which shall be deemed an original, but all of which together shall constitute one and the same instrument. In making proof of this Agreement, it shall not be necessary to produce or account for more than one such counterpart.

IN WITNESS WHEREOF, the parties hereto have executed this Non-Disclosure Agreement by their duly authorized officers or representatives as of the date first set forth above.

MME Houdstermaatschappij B.V.: Bert Rademakers, CEO
{company_name}: {name}, {title}
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        logger.info("Received POST request")
        name = request.form.get("name")
        email = request.form.get("email")
        business = request.form.get("business")
        address = request.form.get("address")
        title = request.form.get("title")
        accept = request.form.get("accept")
        signature_data = request.form.get("signature")

        logger.info(f"Form data: name={name}, email={email}, business={business}, address={address}, title={title}, accept={accept}, signature={signature_data[:50] if signature_data else None}")

        if not accept:
            logger.error("Accept checkbox not checked")
            return "You must accept the NDA!", 400
        if not signature_data or len(signature_data) < 100:
            logger.error("Signature data missing or invalid")
            return "Please provide a valid signature!", 400

        customized_nda = NDA_TEXT.format(
            company_name=business,
            full_address=address,
            name=name,
            title=title
        )
        logger.info(f"Customized NDA excerpt: {customized_nda[:100]}")

        try:
            signature_data = signature_data.split(',')[1]
            signature_img = Image.open(BytesIO(base64.b64decode(signature_data)))
            signature_path = f"signature_{name}.png"
            signature_img.save(signature_path, "PNG")
            logger.info(f"Signature saved: {signature_path}")
        except Exception as e:
            logger.error(f"Signature processing failed: {str(e)}")
            return f"Error processing signature: {str(e)}", 500

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 5, f"Non-Disclosure Agreement\n\nSigned by: {name}\nEmail: {email}\nBusiness: {business}\nAddress: {address}\nTitle: {title}\n\n{customized_nda}")
            pdf.ln(10)
            # Add user's signature
            pdf.image(signature_path, x=100, y=pdf.get_y(), w=50)
            pdf.ln(20)  # Space between signatures
            # Add Bert's signature
            bert_signature_path = os.path.join(app.root_path, 'static', 'bert_signature.png')
            pdf.image(bert_signature_path, x=10, y=pdf.get_y(), w=50)
            pdf_file = f"nda_{name}.pdf"
            pdf.output(pdf_file)
            logger.info(f"PDF generated: {pdf_file}")
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            return f"Error generating PDF: {str(e)}", 500

        email_success = True
        try:
            send_email(email, "You have signed the NDA", "Thank you for signing the NDA with MME Houdstermaatschappij. See attached.", pdf_file)
            logger.info(f"Email sent to client: {email}")
        except Exception as e:
            logger.error(f"Client email failed: {str(e)}")
            email_success = False

        try:
            send_email(EMAIL_ADDRESS, f"{name} signed an NDA", f"{name} from {business} signed the NDA. See attached.", pdf_file)
            logger.info(f"Email sent to sender: {EMAIL_ADDRESS}")
        except Exception as e:
            logger.error(f"Sender email failed: {str(e)}")
            email_success = False

        if email_success:
            return "NDA signed and emailed successfully!"
        else:
            return "NDA signed, but email sending failed. Please contact support.", 200

    return render_template("index.html", nda_text=NDA_TEXT.format(company_name="COMPANY NAME", full_address="FULL ADDRESS", name="NAME", title="TITLE"))

def send_email(to_email, subject, body, attachment):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise ValueError(f"Email credentials missing: EMAIL_ADDRESS={EMAIL_ADDRESS}, EMAIL_PASSWORD={'set' if EMAIL_PASSWORD else 'not set'}")

    SMTP_HOST = "server104.yourhosting.nl"
    SMTP_PORT = 587

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with open(attachment, "rb") as f:
        part = MIMEText(f.read(), "base64", "utf-8")
        filename = os.path.basename(attachment)
        part.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(part)

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            logger.info(f"Attempting SMTP connection to {SMTP_HOST}:{SMTP_PORT}, attempt {attempt + 1}/{max_attempts}")
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
            server.ehlo()
            logger.info("EHLO successful")
            server.starttls()
            logger.info("STARTTLS successful")
            server.ehlo()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            logger.info("Login successful")
            server.send_message(msg)
            logger.info("Message sent")
            server.quit()
            logger.info(f"Email sent successfully to {to_email}")
            break
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication error: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error on attempt {attempt + 1}: {str(e)}")
            if attempt == max_attempts - 1:
                raise Exception(f"SMTP failed after {max_attempts} attempts: {str(e)}")
            time.sleep(3)
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
            if attempt == max_attempts - 1:
                raise Exception(f"Unexpected error after {max_attempts} attempts: {str(e)}")
            time.sleep(3)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
