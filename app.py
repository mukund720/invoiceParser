from flask import Flask, request, jsonify
from invoices.invoice_utils import convert_to_json

app = Flask(__name__)

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
