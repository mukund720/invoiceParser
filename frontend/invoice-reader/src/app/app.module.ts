import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms'; // Import FormsModule

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { FileUploadComponent } from './file-upload/file-upload.component';
import { PdfViewerComponent } from './pdf-viewer/pdf-viewer.component';
import { TextAreasComponent } from './text-areas/text-areas.component';

@NgModule({
  declarations: [
    AppComponent,
    FileUploadComponent,
    PdfViewerComponent,
    TextAreasComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule // Add FormsModule here,
    ReactiveFormsModule // Add ReactiveFormsModule to the imports array

  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
