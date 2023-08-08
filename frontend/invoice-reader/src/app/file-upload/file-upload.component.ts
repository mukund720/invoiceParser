import { Component } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent {
  selectedFile!: File; // Use the non-null assertion operator

  constructor(private apiService: ApiService) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  uploadFile() {
    const formData = new FormData(); // Create a new FormData object
    formData.append('pdf_file', this.selectedFile); // Append the selectedFile to the FormData

    this.apiService.uploadPdf(formData).subscribe(response => {
      // Handle response from backend
    });
  }

}
