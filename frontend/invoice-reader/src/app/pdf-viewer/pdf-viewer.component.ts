import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { ApiService } from '../api.service';
import * as crypto from 'crypto';


@Component({
  selector: 'app-pdf-viewer',
  templateUrl: './pdf-viewer.component.html',
  styleUrls: ['./pdf-viewer.component.scss']
})
export class PdfViewerComponent implements OnInit {
  @ViewChild('pdfCanvas', { static: true }) pdfCanvas!: ElementRef<HTMLCanvasElement>;

  canvas!: HTMLCanvasElement; // Add '!' to indicate that it will be initialized later
  ctx!: CanvasRenderingContext2D; // Add '!' to indicate that it will be initialized later
  images: HTMLImageElement[] = [];

  startX = 0;
  startY = 0;
  endX = 0;
  endY = 0;
  isSelecting = false;
  uniqueTextAreas: { [contentHash: string]: boolean } = {};
  currentColorIndex = 0;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.canvas = this.pdfCanvas.nativeElement;
    if (this.canvas) {
      this.ctx = this.canvas.getContext('2d')!;
      if (!this.ctx) {
        throw new Error("Could not get 2D context for canvas");
      }
    } else {
      throw new Error("Could not find canvas element");
    }
  }



  drawPDF() {
    if (this.images.length > 0) {
      const img = this.images[0];
      this.canvas.width = img.width;
      this.canvas.height = img.height;
      this.ctx.drawImage(img, 0, 0, img.width, img.height);
    }
  }

  onMouseDown(event: MouseEvent) {
    this.startX = event.clientX - this.canvas.getBoundingClientRect().left;
    this.startY = event.clientY - this.canvas.getBoundingClientRect().top;
    this.isSelecting = true;
  }

  onMouseMove(event: MouseEvent) {
    if (this.isSelecting) {
      this.endX = event.clientX - this.canvas.getBoundingClientRect().left;
      this.endY = event.clientY - this.canvas.getBoundingClientRect().top;
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.drawPDF();
      this.ctx.strokeStyle = 'red';
      this.ctx.lineWidth = 2;

      const scaleX = this.canvas.width / this.canvas.offsetWidth;
      const scaleY = this.canvas.height / this.canvas.offsetHeight;

      this.ctx.strokeRect(
        this.startX * scaleX,
        this.startY * scaleY,
        (this.endX - this.startX) * scaleX,
        (this.endY - this.startY) * scaleY
      );
    }
  }

  onMouseUp() {
    this.isSelecting = false;
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.drawPDF();
    const section = {
      startX: Math.min(this.startX, this.endX),
      startY: Math.min(this.startY, this.endY),
      endX: Math.max(this.startX, this.endX),
      endY: Math.max(this.startY, this.endY),
      croppedImage: this.canvas.toDataURL('image/jpeg')
    };

    section.startX *= this.canvas.width / this.canvas.offsetWidth;
    section.startY *= this.canvas.height / this.canvas.offsetHeight;
    section.endX *= this.canvas.width / this.canvas.offsetWidth;
    section.endY *= this.canvas.height / this.canvas.offsetHeight;

    const sectionColor = this.getNextColor();
    this.sendSelectedSection(section);
    this.drawSectionBorder(
      section.startX,
      section.startY,
      section.endX,
      section.endY,
      sectionColor
    );
  }

  sendSelectedSection(section:any) {
    this.apiService.sendSelectedSection(section).subscribe(
      response => {
        if (response.status) {
          const rect = response.response[0];
          this.createUniqueElement(rect, rect, response.type);
        }
        console.log('Retrieved values:', response);
      },
      error => {
        console.error('Error:', error);
      }
    );
  }

  createUniqueElement(content:any, rect:any, type:any) {
    const contentHash = this.hashContent(content);
    if (!this.uniqueTextAreas.hasOwnProperty(contentHash)) {
      const textareasContainer = document.getElementById(
        'textareasContainer'
      ) as HTMLElement;
      let element: HTMLElement;

      if (type === 'table') {
        element = document.createElement(content);
      } else {
        element = document.createElement('textarea');
        element.textContent = content;
      }

      this.uniqueTextAreas[contentHash] = true;
      textareasContainer.appendChild(element);
    }
  }

  drawSectionBorder(startX:any, startY:any, endX:any, endY:any, color:any) {
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(startX, startY, endX - startX, endY - startY);
  }

  hashContent(content:string) {
    const hash = crypto.createHash('md5').update(content).digest('hex');
    return hash;
  }

  highlightMatchingSelection(rect:any, contentRectangles:any) {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.drawPDF();
    this.ctx.strokeStyle = 'red';
    this.ctx.lineWidth = 2;

    if (contentRectangles) {
      contentRectangles.forEach((contentRect: { startX: number; startY: number; width: number; height: number; }) => {
        this.ctx.strokeRect(
          contentRect.startX,
          contentRect.startY,
          contentRect.width,
          contentRect.height
        );
      });
    }

    this.ctx.strokeRect(rect.startX, rect.startY, rect.width, rect.height);
  }

  highlightSelection(rect: { startX: number; startY: number; width: number; height: number; }) {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.drawPDF();

    this.ctx.strokeStyle = 'red';
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(rect.startX, rect.startY, rect.width, rect.height);
  }

  getNextColor() {
    const sectionColors = ['red', 'blue', 'green', 'orange', 'purple'];
    const color = sectionColors[this.currentColorIndex];
    this.currentColorIndex = (this.currentColorIndex + 1) % sectionColors.length;
    return color;
  }


  uploadFile(event: any) {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('pdf_file', file);

    this.apiService.uploadPdf(formData).subscribe(
      response => {
        if (response.success) {
          this.images = response.images.map((imgBase64: string) => {
            const img = new Image();
            img.onload = () => {
              this.drawPDF();
            };
            img.src = 'data:image/jpeg;base64,' + imgBase64;
            return img;
          });
        } else {
          console.error('Error:', response.error);
        }
      },
      error => {
        console.error('Error:', error);
      }
    );
  }

  adjustCanvasSize() {
    if (this.canvas) {
      const containerWidth = this.canvas.parentElement?.clientWidth;
      if (containerWidth) {
        const containerHeight = containerWidth * (this.canvas.height / this.canvas.width);
        this.canvas.width = containerWidth;
        this.canvas.height = containerHeight;
        this.drawPDF();
      }
    }
  }


  ngAfterViewInit() {
    this.adjustCanvasSize();
  }

  ngOnDestroy() {
    window.removeEventListener('resize', this.adjustCanvasSize);
  }
}

