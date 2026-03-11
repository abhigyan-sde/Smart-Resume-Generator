import {
  Component,
  Input,
  Output,
  OnChanges,
  SimpleChanges,
  ViewChildren,
  QueryList,
  ElementRef,
  AfterViewInit,
  EventEmitter,
} from '@angular/core';
import { PDFDocumentProxy, getDocument, GlobalWorkerOptions } from 'pdfjs-dist';
import PdfJsWorker from 'pdfjs-dist/build/pdf.worker.min.mjs?worker';
import { PhysicalSegment, LogicalLine } from '../model/resume-parser.model';

@Component({
  selector: 'app-resume-viewer',
  templateUrl: './viewer.component.html',
  styleUrls: ['./viewer.component.css'],
})
export class ViewerComponent implements OnChanges, AfterViewInit {
  @Input() pdfUrl: string | null = null;
  @Output() lineMap = new EventEmitter<LogicalLine[]>();

  @ViewChildren('pdfCanvas')
  pdfCanvas!: QueryList<ElementRef<HTMLCanvasElement>>;

  pdfDoc: PDFDocumentProxy | null = null;
  pages: number[] = [];

  private logicalLines: LogicalLine[] = [];
  private lineId = 1;

  constructor() {
    GlobalWorkerOptions.workerPort = new PdfJsWorker();
  }

  ngAfterViewInit() {
    this.renderPages();
    setTimeout(() => this.extractAllPagesText(), 0);
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
      this.pages = Array.from(
        { length: this.pdfDoc.numPages },
        (_, i) => i + 1
      );

      this.logicalLines = [];
      this.lineId = 1;

      setTimeout(() => this.renderPages(), 0);
      setTimeout(() => this.extractAllPagesText(), 0);
    } catch (err) {
      console.error('Error loading PDF:', err);
      this.pages = [];
    }
  }

  private async renderPages() {
    if (!this.pdfDoc || !this.pdfCanvas?.length) return;

    const firstPage = await this.pdfDoc.getPage(1);
    const containerWidth =
      this.pdfCanvas.first.nativeElement.parentElement!.clientWidth;

    const viewport = firstPage.getViewport({ scale: 1 });
    const scale = containerWidth / viewport.width;

    this.pdfCanvas.forEach(async (canvasRef, index) => {
      const pageNumber = index + 1;
      const page = await this.pdfDoc!.getPage(pageNumber);

      const scaledViewport = page.getViewport({ scale });
      const canvas = canvasRef.nativeElement;
      canvas.width = scaledViewport.width;
      canvas.height = scaledViewport.height;

      const ctx = canvas.getContext('2d')!;
      await page.render({
        canvasContext: ctx,
        viewport: scaledViewport,
        canvas,
      }).promise;
    });
  }

  private async extractAllPagesText(): Promise<void> {
    if (!this.pdfDoc) return;

    this.logicalLines = [];
    this.lineId = 1;

    for (let pageNum = 1; pageNum <= this.pdfDoc.numPages; pageNum++) {
      const page = await this.pdfDoc.getPage(pageNum);
      const textContent = await page.getTextContent();

      const segments: PhysicalSegment[] = [];

      for (const item of textContent.items as any[]) {
        const t = item.transform;
        segments.push({
          page: pageNum,
          y: Math.round(t[5]),
          xStart: t[4],
          xEnd: t[4] + item.width,
          rawText: item.str ?? '',
        });
      }

      segments.sort((a, b) => b.y - a.y);

      const groupedByY = this.groupSegmentsByY(segments);
      this.processLogicalLines(groupedByY);
    }

    this.lineMap.emit(this.logicalLines)
  }

  private groupSegmentsByY(
    segments: PhysicalSegment[]
  ): Record<number, PhysicalSegment[]> {
    const map: Record<number, PhysicalSegment[]> = {};

    for (const seg of segments) {
      if (!map[seg.y]) map[seg.y] = [];
      map[seg.y].push(seg);
    }

    for (const y in map) {
      map[y].sort((a, b) => a.xStart - b.xStart);
    }

    return map;
  }

  private processLogicalLines(groupedByY: Record<number, PhysicalSegment[]>) {
    let buffer = '';
    let bucket: PhysicalSegment[] = [];

    const sortedYs = Object.keys(groupedByY)
      .map(Number)
      .sort((a, b) => b - a);

    for (const y of sortedYs) {
      const row = groupedByY[y];
      const text = this.buildRowText(row);
      if (!text) continue;

      const first = text[0];
      const lastPrev = buffer.trim().slice(-1);

      if (this.isBullet(first) || (this.isUpper(first) && this.isTerminal(lastPrev) && buffer.length > 0)) {
        this.commitLine(buffer, bucket);
        buffer = '';
        bucket = [];
      }

      if (buffer)
        buffer += ' ';

      buffer += text;
      bucket.push(...row);
    }

    this.commitLine(buffer, bucket);
  }

  private commitLine(text: string, segments: PhysicalSegment[]) {
    if (!text.trim()) return;
    this.logicalLines.push({
      lineId: this.lineId++,
      text: text.trim(),
      segments,
    });
  }

  private buildRowText(row: PhysicalSegment[]): string {
    if (!row.length) return '';

    let text = row[0].rawText;
    let prev = row[0];

    for (let i = 1; i < row.length; i++) {
      const curr = row[i];

      const gap = curr.xStart - prev.xEnd;

      // heuristic thresholds (tuned for resume PDFs)
      if (gap > 6) {
        text += ' ';
      }

      text += curr.rawText;
      prev = curr;
    }

    return this.normalizeText(text);
  }

  private normalizeText(text: string): string {
    return this.fixBrokenWords(text
      // collapse excessive spaces
      .replace(/\s{2,}/g, ' ')
      // fix space before punctuation
      .replace(/\s+([.,:;])/g, '$1')
      // fix bullet spacing
      .replace(/^•\s*/, '• ')
      // trim
      .trim());
  }
  private fixBrokenWords(text: string): string {
    return text.replace(/\b([A-Za-z])\s+([a-z]{2,})\b/g, '$1$2');
  }

  private isUpper(c: string) {
    return /[A-Z]/.test(c);
  }

  private isBullet(c: string) {
    return ['•', '●', '‣', '▪', '◦', '*'].some(b => c.startsWith(b));
  }

  private isTerminal(c: string) {
    return ['.', '!', '?'].includes(c) || /[A-Za-z0-9]/.test(c);
  }
}
