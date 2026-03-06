import {
  Component,
  Input,
  Output,
  EventEmitter,
  OnChanges,
  SimpleChanges
} from '@angular/core';

@Component({
  selector: 'app-text-preview',
  templateUrl: './text-preview.component.html',
  styleUrls: ['text-preview.component.css']
})
export class ResumeTextPreviewComponent implements OnChanges {
  @Input() originalLines: Record<number, string> = {};
  @Input() updatedLines: Record<number, string> = {};

  @Output() resumeTextChanged = new EventEmitter<Record<number, string>>();

  /** Final merged view shown to user */
  displayLines: { lineId: number; text: string; isUpdated: boolean }[] = [];

  ngOnChanges(_: SimpleChanges): void {
    this.rebuildDisplayLines();
  }

  private rebuildDisplayLines(): void {
    this.displayLines = Object.keys(this.originalLines)
      .map(id => Number(id))
      .sort((a, b) => a - b)
      .map(lineId => ({
        lineId,
        text: this.updatedLines[lineId] ?? this.originalLines[lineId],
        isUpdated: lineId in this.updatedLines
      }));
  }

  onEdit(lineId: number, value: string): void {
    this.updatedLines = {
      ...this.updatedLines,
      [lineId]: value
    };

    this.resumeTextChanged.emit(this.updatedLines);
    this.rebuildDisplayLines();
  }
}
