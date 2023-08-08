import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://127.0.0.1:8000/'; // Replace with your backend API URL

  constructor(private http: HttpClient) {}

  uploadPdf(formData: FormData): Observable<any> {
    const url = `${this.baseUrl}/process_pdf`;
    return this.http.post(url, formData);
  }

  sendSelectedSection(section: any): Observable<any> {
    const url = `${this.baseUrl}/process_section`;
    return this.http.post(url, section);
  }
}
