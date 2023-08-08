import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { FileUploadComponent } from './file-upload/file-upload.component';
import { PdfViewerComponent } from './pdf-viewer/pdf-viewer.component';
import { TextAreasComponent } from './text-areas/text-areas.component';

const routes: Routes = [
  { path: 'upload', component: FileUploadComponent },
  { path: 'viewer', component: PdfViewerComponent },
  { path: 'text-areas', component: TextAreasComponent },
  { path: '', redirectTo: '/upload', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
