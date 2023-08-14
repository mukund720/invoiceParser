import re
import pdfplumber
import pytesseract
from io import BytesIO
import time
from PIL import Image
import fitz  # PyMuPDF
import pytesseract
import json

def is_pdf(data):
    return data.startswith(b'%PDF')

def is_numeric_string(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def convert_number_string_to_number(value):
    return float(value) if '.' in value else int(value)

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return '\n'.join([page.extract_text() for page in pdf.pages])

def extract_text_from_image(image):
    # Convert the image to grayscale for better OCR results
    gray_image = image.convert("L")

    # Use pytesseract to extract text from the grayscale image
    extracted_text = pytesseract.image_to_string(gray_image)

    return extracted_text

def format_processing_time(processing_time):
    if processing_time < 1:
        return f"{round(processing_time * 1000)} ms"
    elif processing_time < 60:
        return f"{round(processing_time, 2)} s"
    else:
        minutes, seconds = divmod(processing_time, 60)
        return f"{int(minutes)} min {seconds:.2f} s"
    

column_headers = ["Sl.No", "Part No", "Product Description", "Qty (per)", "Rate", "Amount", "CGST", "SGST", "IGST", "UGST", "CESS", "Other Tax", "Total Tax", "Amount", "Balance", "PO Quantity"]
def extract_items(text, column_headers):
    # Create the row pattern dynamically based on the column headers
    row_pattern = r"(?m)^\d+\s+(" + r"\s+".join([r"(.+?)"] * len(column_headers)) + r")\s*$"

    # Search for the table pattern in the text
    table_matches = re.findall(row_pattern, text)
    items = []
    for match in table_matches:
        item_data = {}
        for i, header in enumerate(column_headers):
            item_data[header] = match[i].strip()
        items.append(item_data)
    return items

def extract_summary_data(text):
    total_amount_pattern = r"Total Amount:\s+([\d.]+)"
    cgst_pattern = r"Total CGST\s+([\d.]+)"
    sgst_pattern = r"Total UGST\s+([\d.]+)"
    cess_pattern = r"Total CESS\s+([\d.]+)"
    other_tax_pattern = r"TDS Amount\s+([\d.]+)"
    total_gst_pattern = r"Total Other Tax\s+([\d.]+)"
    grand_total_pattern = r"Total\s+([\d.]+)"
    remaining_balance_pattern = r"Remaining Balance\s+([\d.]+)"
    round_off_total_pattern = r"Round Off Total:\s+([\d.]+)"
    amount_chargable_pattern = r"Amount Chargable \(in words\):\s+([\w\s]+)"

    total_amount_match = re.search(total_amount_pattern, text)
    cgst_match = re.search(cgst_pattern, text)
    sgst_match = re.search(sgst_pattern, text)
    cess_match = re.search(cess_pattern, text)
    other_tax_match = re.search(other_tax_pattern, text)
    total_gst_match = re.search(total_gst_pattern, text)
    grand_total_match = re.search(grand_total_pattern, text)
    remaining_balance_match = re.search(remaining_balance_pattern, text)
    round_off_total_match = re.search(round_off_total_pattern, text)
    amount_chargable_match = re.search(amount_chargable_pattern, text)

    total_amount = total_amount_match.group(1) if total_amount_match else None
    cgst = cgst_match.group(1) if cgst_match else None
    sgst = sgst_match.group(1) if sgst_match else None
    cess = cess_match.group(1) if cess_match else None
    other_tax = other_tax_match.group(1) if other_tax_match else None
    total_gst = total_gst_match.group(1) if total_gst_match else None
    adjusted_amount = None
    grand_total = grand_total_match.group(1) if grand_total_match else None
    remaining_balance = remaining_balance_match.group(1) if remaining_balance_match else None
    total_other_tax = None
    round_off_total = round_off_total_match.group(1) if round_off_total_match else None
    amount_chargable = amount_chargable_match.group(1) if amount_chargable_match else None

    summary_data = {
        "Total_Amount": total_amount,
        "CGST": cgst,
        "SGST": sgst,
        "CESS": cess,
        "Other_Tax": other_tax,
        "Total_GST": total_gst,
        "Adjusted_Amount": adjusted_amount,
        "Grand_Total": grand_total,
        "Remaining_Balance": remaining_balance,
        "Total_Other_Tax": total_other_tax,
        "Round_Off_Total": round_off_total,
        "Amount_Chargable_in_words": amount_chargable,
    }
    return summary_data


def extract_vendor(text):
    vendor_details_pattern = r"VENDOR DETAILS\s*([\w\s.,-]+)"
    vendor_details_match = re.search(vendor_details_pattern, text)
    
    return vendor_details_match.group(1).strip() if vendor_details_match else None

def extract_custom_ship_location_name(text):
    ship_location_pattern = r"Custom Ship Location Name:\s*(.+?)\s+Invoice no:"
    ship_location_match = re.search(ship_location_pattern, text)
    
    return ship_location_match.group(1).strip() if ship_location_match else None

def extract_custom_bill_location_name(text):
    bill_location_pattern = r"Custom Bill Location Name:\s*(.+?)\s+GSTIN:"
    bill_location_match = re.search(bill_location_pattern, text)
    
    return bill_location_match.group(1).strip() if bill_location_match else None

def extract_invoice_number(text):
    invoice_number_pattern = r"Invoice no:\s+(.+?)\n"
    invoice_number_match = re.search(invoice_number_pattern, text)
    
    return invoice_number_match.group(1).strip() if invoice_number_match else None

def extract_date(text):
    date_pattern = r"Date:\s+(.+?)\n"
    date_match = re.search(date_pattern, text)
    
    return date_match.group(1).strip() if date_match else None

def extract_raisers_and_approvers(text):
    raiser_pattern = r'RAISER DETAILS\nNo\s+Contact Person\s+Email\n\d+\s+(.*?)\s+([\w\.-]+@[\w\.-]+)'
    approver_pattern = r'APPROVER DETAILS\nNo\s+Approved By\s+Email\s+Approved Date\n\d+\s+(.*?)\s+([\w\.-]+@[\w\.-]+)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'
    raiser_matches = re.findall(raiser_pattern, text)
    approver_matches = re.findall(approver_pattern, text)
    
    raisers = [{"name": name.strip(), "email": email.strip()} for name, email in raiser_matches]
    approvers = [{"name": name.strip(), "email": email.strip(), "approved_date": date.strip()} for name, email, date in approver_matches]
    
    return raisers, approvers

def convert_to_json(data):
    start_time = time.time()
    if is_pdf(data):
        pdf_file = BytesIO(data)
        pdf_text = extract_text_from_pdf(pdf_file)
        invoice_number = extract_invoice_number(pdf_text)
        date = extract_date(pdf_text)
        vendor_name = extract_vendor(pdf_text)
        custom_ship_location_name = extract_custom_ship_location_name(pdf_text)
        custom_bill_location_name = extract_custom_bill_location_name(pdf_text)
        items = extract_items(pdf_text, column_headers)
        summary_data = extract_summary_data(pdf_text)
        raiser_data, approver_data = extract_raisers_and_approvers(pdf_text)
    else:
        image_file = BytesIO(data)
        image_text = extract_text_from_image(image_file)
        invoice_number = extract_invoice_number(image_text)
        date = extract_date(image_text)
        vendor_name = extract_vendor(image_text)
        custom_ship_location_name = extract_custom_ship_location_name(image_text)
        custom_bill_location_name = extract_custom_bill_location_name(image_text)
        items = extract_items(image_text, column_headers)
        summary_data = extract_summary_data(image_text)
        raiser_data, approver_data = extract_raisers_and_approvers(image_text)

    def replace_none_with_empty_string(value):
        return "" if value is None else value

    def replace_none_with_zero(value):
        return 0 if value is None else value

    invoice_number = replace_none_with_empty_string(invoice_number)
    date = replace_none_with_empty_string(date)
    vendor_name = replace_none_with_empty_string(vendor_name)
    custom_ship_location_name = replace_none_with_empty_string(custom_ship_location_name)
    custom_bill_location_name = replace_none_with_empty_string(custom_bill_location_name)

    for item in items:
        for key, value in item.items():
            if key in ["Sl.No", "Received qty", "Unit Price", "CGST", "SGST", "IGST", "UGST", "CESS", "Other Tax", "Total Tax", "Amount", "Balance", "PO Quantity"]:
                if isinstance(value, str) and is_numeric_string(value):
                    item[key] = convert_number_string_to_number(value)
                else:
                    item[key] = replace_none_with_zero(value)
            else:
                item[key] = replace_none_with_empty_string(value)

    for key, value in summary_data.items():
        if isinstance(value, str) and is_numeric_string(value):
            summary_data[key] = convert_number_string_to_number(value)
        else:
            summary_data[key] = replace_none_with_zero(value)

    for raiser in raiser_data:
        raiser["name"] = replace_none_with_empty_string(raiser["name"])
        raiser["email"] = replace_none_with_empty_string(raiser["email"])

    for approver in approver_data:
        approver["name"] = replace_none_with_empty_string(approver["name"])
        approver["email"] = replace_none_with_empty_string(approver["email"])
        approver["approved_date"] = replace_none_with_empty_string(approver["approved_date"])
    
    end_time = time.time()
    processing_time = end_time - start_time

    invoice_data = {
        "message": "data parsed",
        "status": True,
        "processing_time": format_processing_time(processing_time),
        "response": [{
            "invoice_number": invoice_number,
            "date": date,
            "vendor_name": vendor_name,
            "custom_ship_location_name": custom_ship_location_name,
            "custom_bill_location_name": custom_bill_location_name,
            "items": items,
            "summary_data": summary_data,
            "raiser_data": raiser_data,
            "approver_data": approver_data
        }]
    }
    return invoice_data
# Extract text from PDF using PyMuPDF
def extract_text_from_pdf(pdf_file):
    extracted_text = ''
    pdf_document = fitz.open(pdf_file)
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        page_text = page.get_text()
        extracted_text += page_text
    pdf_document.close()
    return extracted_text


def extract_labels_and_values(text):
    lines = text.split('\n')
    labels_values = {}
    current_label = None

    for line in lines:
        line = line.strip()  # Remove leading and trailing spaces
        # Check if the line contains a colon to determine if it's a label
        if ':' in line:
            label, value = line.split(':', 1)
            current_label = label.strip()
            labels_values[current_label] = value.strip()
        elif '-' in line:
            parts = line.split('-', 1)
            if len(parts) >= 2:
                label = parts[0].strip()
                value = parts[1].strip()
                if current_label is not None:
                    labels_values[current_label] += ' ' + label
                    label = current_label
                    current_label = None
                labels_values[label] = value
        elif current_label is not None:
            # Append to the current label's value if no colon or dash is present
            labels_values[current_label] += ' ' + line
        else:
            # No current label, treat this as a label itself
            if line:
                labels_values[line] = ""

    # Find a label that contains the word "Date" and extract its value
    date_label = next((label for label in labels_values.keys() if 'Date' in label), None)
    if date_label:
        date_value = labels_values[date_label]
        # Remove the label from the dictionary
        del labels_values[date_label]

        # Additional processing to extract the date value
        date_pattern = r'(\w{3} \d{2}, \d{4})'  # Format: "Jun 15, 2023"
        match = re.search(date_pattern, date_value)
        if match:
            labels_values['Date'] = match.group(1)

    return labels_values

