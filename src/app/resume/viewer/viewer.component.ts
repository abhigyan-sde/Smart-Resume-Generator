import {
  Component,
  Input,
  OnChanges,
  SimpleChanges,
  ViewChildren,
  QueryList,
  ElementRef,
  AfterViewInit,
} from '@angular/core';
import { PDFDocumentProxy, getDocument, GlobalWorkerOptions } from 'pdfjs-dist';
import PdfJsWorker from 'pdfjs-dist/build/pdf.worker.min.mjs?worker';

@Component({
  selector: 'app-resume-viewer',
  templateUrl: './viewer.component.html',
  styleUrls: ['./viewer.component.css'],
})
export class ViewerComponent implements OnChanges, AfterViewInit {
  @Input() pdfUrl: string | null = null;
  @ViewChildren('pdfCanvas') pdfCanvas!: QueryList<ElementRef<HTMLCanvasElement>>;

  pdfDoc: PDFDocumentProxy | null = null;
  pages: number[] = [];

  constructor() {
    // assign the worker properly
    GlobalWorkerOptions.workerPort = new PdfJsWorker();
  }

  ngAfterViewInit() {
    this.renderPages();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['pdfUrl']) {
      if (this.pdfUrl) {
        this.loadPdf(this.pdfUrl);
      } else {
        this.pages = [];
        this.pdfDoc = null;
      }
    }
  }

  private async loadPdf(url: string) {
    try {
      this.pdfDoc = await getDocument(url).promise;
      this.pages = Array.from({ length: this.pdfDoc.numPages }, (_, i) => i + 1);

      setTimeout(() => this.renderPages(), 0);
    } catch (err) {
      console.error('Error loading PDF:', err);
      this.pages = [];
    }
  }

  private async renderPages() {
  if (!this.pdfDoc || !this.pdfCanvas) return;

  // Compute a fixed scale based on the first page width
  const firstPage = await this.pdfDoc.getPage(1);
  const containerWidth = this.pdfCanvas.first.nativeElement.parentElement!.clientWidth;
  const viewport = firstPage.getViewport({ scale: 1 });
  const scale = containerWidth / viewport.width; // uniform scale for all pages

  // Render all pages with the same scale
  this.pdfCanvas.forEach(async (canvasRef, index) => {
    const pageNumber = index + 1;
    const page = await this.pdfDoc!.getPage(pageNumber);

    const scaledViewport = page.getViewport({ scale });
    const canvas = canvasRef.nativeElement;
    canvas.width = scaledViewport.width;
    canvas.height = scaledViewport.height;

    const ctx = canvas.getContext('2d')!;
    await page.render({ canvas, viewport: scaledViewport, canvasContext: ctx }).promise;
  });
}

}
