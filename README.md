# invoiceParser

#how to run
install all library required

python3 app.py

open postman input formdata "invoice_pdf" as pdf or image file

and you will get response in json

```bash

{
    "message": "data parsed",
    "processing_time": "883 ms",
    "response": [
        {
            "approver_data": [],
            "custom_bill_location_name": "",
            "custom_ship_location_name": "",
            "date": "",
            "invoice_number": "",
            "items": [
                {
                    "Amount": "books(PRD262)",
                    "Balance": 21.0,
                    "CESS": 1396.55,
                    "CGST": 36.89,
                    "IGST": 126.48,
                    "Other Tax": 2,
                    "PO Quantity": 22,
                    "Part No": "PCAT14",
                    "Product Description": "hood(PRD254)",
                    "Qty (per)": "17.00",
                    "Rate": "62",
                    "SGST": 52.7,
                    "Sl.No": "PCAT14 hood(PRD254) 17.00 62 1054 36.89 52.7 126.48 126.48 1396.55\n2 cat001001 books(PRD262) 21.00 22 462 41.58 41.58 13.86 559.02",
                    "Total Tax": "cat001001",
                    "UGST": 126.48
                },
                {
                    "Amount": 27.0,
                    "Balance": 32,
                    "CESS": 4,
                    "CGST": 20.88,
                    "IGST": 6.96,
                    "Other Tax": 3254,
                    "PO Quantity": 864,
                    "Part No": "kajal1031",
                    "Product Description": "MACBOOK(PRD156)",
                    "Qty (per)": "8.00",
                    "Rate": "29",
                    "SGST": 20.88,
                    "Sl.No": "kajal1031 MACBOOK(PRD156) 8.00 29 232 20.88 20.88 6.96 280.72\n4 3254 NoteBooks(PROD001) 27.00 32 864 77.76 77.76 25.92 1045.44",
                    "Total Tax": "NoteBooks(PROD001)",
                    "UGST": 280.72
                },
                {
                    "Amount": "mac",
                    "Balance": "book",
                    "CESS": 1216.35,
                    "CGST": 32.13,
                    "IGST": 110.16,
                    "Other Tax": 6,
                    "PO Quantity": "pro(PRDHM000899440090",
                    "Part No": "Note",
                    "Product Description": "books(PRD003)",
                    "Qty (per)": "17.00",
                    "Rate": "54",
                    "SGST": 45.9,
                    "Sl.No": "Note books(PRD003) 17.00 54 918 32.13 45.9 110.16 110.16 1216.35\n6 CAIC9014 mac book pro(PRDHM000899440090 23.00 76 1748 61.18 87.4 209.76 209.76 2316.1",
                    "Total Tax": "CAIC9014",
                    "UGST": 110.16
                }
            ],
            "raiser_data": [],
            "summary_data": {
                "Adjusted_Amount": 0,
                "Amount_Chargable_in_words": 0,
                "CESS": 493.14,
                "CGST": 270.42,
                "Grand_Total": 5278,
                "Other_Tax": 126.48,
                "Remaining_Balance": 6687.7,
                "Round_Off_Total": 0,
                "SGST": 326.22,
                "Total_Amount": 0,
                "Total_GST": 446.4,
                "Total_Other_Tax": 0
            },
            "vendor_name": ""
        }
    ],
    "status": true
}
```
