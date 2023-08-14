import re
from invoices.invoice_utils import convert_to_json,extract_labels_and_values,extract_text_from_pdf
from flask import Flask, render_template, render_template, request, jsonify
from pdf2image import convert_from_bytes
import io
import base64
from PIL import Image,ImageDraw
import pytesseract
import tempfile
import os
app = Flask(__name__)

uploaded_images = []  # To store the loaded images globally


@app.route('/')
def index():
    return render_template('index.html')

# Define the save_data endpoint
@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.get_json()
    pdf_data = data.get('pdfData')
    label_text_area_map = data.get('labelTextAreaMap')

    if pdf_data and label_text_area_map:
        # Process the PDF data and label-textarea associations
        # You can save the PDF and label associations in your desired way here
        
        # Assuming you save successfully
        response = {
            'response':[label_text_area_map],
            'status': True,
            'message': 'Mapped'
        }
    else:
        response = {
             'response':[],
            'status': False,
            'message': 'Data missing'
        }
    
    return jsonify(response)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    uploaded_file = request.files['pdf_file']
    all_labels_values = []

    if uploaded_file.filename != '':
        pdf_bytes = uploaded_file.read()

        # Save PDF bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_pdf_file:
            temp_pdf_file.write(pdf_bytes)

        try:
            images = convert_from_bytes(pdf_bytes)
            uploaded_images.extend(images)
            # Extract text from the temporary PDF file
            extracted_text = extract_text_from_pdf(temp_pdf_file.name)

            # Process the extracted text and labels/values
            extracted_labels_values = extract_labels_and_values(extracted_text)
            all_labels_values.append(extracted_labels_values)

            image_data = []

            for image in images:
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_data = buffered.getvalue()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                image_data.append(img_base64)

            return jsonify({'success': True, 'images': image_data, 'labels_values': all_labels_values})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e), 'labels_values': all_labels_values})

        finally:
            # Delete the temporary PDF file
            temp_pdf_file.close()
            os.remove(temp_pdf_file.name)

    return jsonify({'success': False, 'error': 'No file uploaded', 'labels_values': all_labels_values})

def extract_labels_and_values_from_pdf(pdf_data):
    labels_values = convert_to_json(pdf_data)
    # if pdf_file and pdf_file.filename.endswith('.pdf'):
    #             # Read the PDF file contents
    #             pdf_data = pdf_file.read()

    #             # Process the PDF data using the invoice_utils.py module
    #             labels_values = convert_to_json(pdf_data)

    return labels_values

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
    labels_values=[]
    if uploaded_images:
        selected_image = uploaded_images[0]
        extracted_text, word_boxes = extract_text_and_boxes_from_section(selected_image, section)
        
        if extracted_text:
            labels_values = extract_labels_and_values(extracted_text)
            image_with_boxes = draw_boxes_on_image(selected_image, word_boxes)
            buffered = io.BytesIO()
            image_with_boxes.save(buffered, format="JPEG")
            img_with_boxes_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            if is_text_table(extracted_text[0]):  # Check the extracted text (first element of the tuple)
                html_table = generate_html_table(extracted_text[0])
                return jsonify({'message': 'parsed table','labels_values':labels_values, 'type': 'table', 'response': html_table, 'status': True, 'image_with_boxes': img_with_boxes_base64}), 200
            else:
                return jsonify({'message': 'parsed text','labels_values':labels_values, 'type': 'string', 'response': [extracted_text], 'status': len(extracted_text[0]) > 0, 'image_with_boxes': img_with_boxes_base64}), 200
        else:
            return jsonify({'message': 'parsed text','labels_values':labels_values, 'type': 'error', 'response': [], 'status': False}), 200
    else:
        return jsonify({'message': 'parsed text','labels_values':labels_values, 'type': 'error', 'response': [], 'status': False}), 200


def draw_boxes_on_image(image, word_boxes):
    img_with_boxes = image.copy()
    draw = ImageDraw.Draw(img_with_boxes)
    
    for box in word_boxes.splitlines():
        box = box.split()
        left, top, right, bottom = int(box[1]), int(box[2]), int(box[3]), int(box[4])
        draw.rectangle([left, top, right, bottom], outline="red", width=2)
    
    return img_with_boxes

def extract_text_and_boxes_from_section(selected_image, section):
    try:
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
        extracted_text = pytesseract.image_to_string(cropped_img, output_type=pytesseract.Output.STRING)
        word_boxes = pytesseract.image_to_boxes(cropped_img, output_type=pytesseract.Output.BYTES)
        
        return extracted_text, word_boxes
    except Exception as e:
        return "", f"Error extracting text: {e}"

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
