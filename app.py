import re
from invoices.invoice_utils import convert_to_json
from flask import Flask, render_template, render_template, request, jsonify
from pdf2image import convert_from_bytes
import io
import base64
from PIL import Image
import pytesseract


app = Flask(__name__)

uploaded_images = []  # To store the loaded images globally


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    uploaded_file = request.files['pdf_file']
    if uploaded_file.filename != '':
        pdf_bytes = uploaded_file.read()
        images = convert_from_bytes(pdf_bytes)
        uploaded_images.extend(images)

        image_data = []

        for image in images:
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_data = buffered.getvalue()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            image_data.append(img_base64)

        return jsonify({'success': True, 'images': image_data})
    return jsonify({'success': False, 'error': 'No file uploaded'})

# ... (other route definitions and functions)

def is_text_table(text):
    # Define regular expressions to match common table-related keywords
    table_keywords = ['S.No.', 'Part No.', 'Rate', 'Amount', 'header', 'data']
    
    # Convert the text to lowercase for case-insensitive matching
    lower_text = text.lower()
    
    # Check if any of the table keywords are present in the text
    for keyword in table_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', lower_text):
            return True
            
    return False

@app.route('/process_section', methods=['POST'])
def process_section():
    section = request.json
    if uploaded_images:
        selected_image = uploaded_images[0]
        extracted_text = extract_text_from_section(selected_image, section)
        
        if is_text_table(extracted_text):
            html_table = generate_html_table(extracted_text)
            return jsonify({'message': 'parsed table', 'type': 'table', 'response': html_table, 'status': True}), 200
        else:
            return jsonify({'message': 'parsed text', 'type': 'string', 'response': [extracted_text], 'status': len(extracted_text) > 0}), 200
    else:
        return jsonify({'message': 'parsed text', 'type': 'error', 'response': [], 'status': False}), 200


def extract_text_from_section(selected_image, section):
    try:
        # Get the coordinates for cropping
        startX = section['startX']
        startY = section['startY']
        endX = section['endX']
        endY = section['endY']
        
        # Decode the Base64 image data
        cropped_image_data = base64.b64decode(
            section['croppedImage'].split(',')[1])

        # Load the image using PIL
        img = Image.open(io.BytesIO(cropped_image_data))

        # Check and adjust coordinates to ensure they are within image bounds
        img_width, img_height = img.size
        startX = max(0, min(startX, img_width - 1))
        startY = max(0, min(startY, img_height - 1))
        endX = max(0, min(endX, img_width))
        endY = max(0, min(endY, img_height))

        # Crop the image
        cropped_img = img.crop((startX, startY, endX, endY))

        # Perform OCR on the cropped image
        extracted_text = pytesseract.image_to_string(cropped_img)
        return extracted_text
    except Exception as e:
        return f"Error extracting text: {e}"

def generate_html_table(table_text):
    # Parse the table_text and generate an HTML table
    # For demonstration purposes, let's create a simple HTML table
    table_html = '<table border="1">'
    rows = table_text.split('\n')
    for row in rows:
        table_html += '<tr>'
        cells = row.split('\t')
        for cell in cells:
            table_html += f'<td>{cell}</td>'
        table_html += '</tr>'
    table_html += '</table>'
    
    return table_html


@app.route('/invoice_data', methods=['GET', 'POST'])
def get_invoice_data():
    if request.method == 'GET':
        # Handle GET request (if needed)
        return jsonify({'message': 'This endpoint supports POST requests. Please send a POST request with a PDF file.'})

    elif request.method == 'POST':
        try:
            # Check if the request contains a file named 'invoice_pdf'
            if 'invoice_pdf' not in request.files:
                return jsonify({'message': 'No PDF file found in the request.', "response": [], "status": False}), 200

            pdf_file = request.files['invoice_pdf']

            # Check if the file is a PDF
            if pdf_file.filename == '':
                return jsonify({'message': 'No selected file.', "response": [], "status": False}), 200

            if pdf_file and pdf_file.filename.endswith('.pdf'):
                # Read the PDF file contents
                pdf_data = pdf_file.read()

                # Process the PDF data using the invoice_utils.py module
                invoice_data = convert_to_json(pdf_data)

                # Return the processed data as JSON response
                return jsonify(invoice_data), 200

            else:
                return jsonify({'message': 'Invalid file format. Please upload a PDF file.', "response": [], "status": False}), 200

        except Exception as e:
            # Handle any other unexpected exceptions
            return jsonify({'message': 'An error occurred while processing the request.', 'errorDetails': str(e), "response": [], "status": False}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
