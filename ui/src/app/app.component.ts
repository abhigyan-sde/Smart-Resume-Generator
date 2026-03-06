import { Component } from '@angular/core';
import { UploadComponent } from './resume/upload/upload.component';
import { ViewerComponent } from './resume/viewer/viewer.component';
import { ResumeEvaluationResult } from './resume/model/resume-evaluation-result.model';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatRadioModule } from '@angular/material/radio';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDividerModule } from '@angular/material/divider';
import { MatToolbar } from '@angular/material/toolbar';
import { ResumeDraft } from './resume/model/resume-parser.model';
import { MatTabsModule } from '@angular/material/tabs';
import { SuggestionsComponent } from './resume/suggestions/suggestions.component';
import { ResumeTextPreviewComponent } from './resume/text-preview/text-preview.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    UploadComponent,
    ViewerComponent,
    FormsModule,
    MatCardModule,
    MatToolbar,
    MatButtonModule,
    MatRadioModule,
    MatFormFieldModule,
    MatInputModule,
    MatDividerModule,
    MatTabsModule,
    SuggestionsComponent,
    ResumeTextPreviewComponent
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'smart_resume_ui';

  pdfSrc: string | null = null;
  evaluation: ResumeEvaluationResult | null = null;

  /** Parsed + editable resume */
  resumeDraft: ResumeDraft | null = null;

  originalLinesForPreview: Record<number, string> = {};
  updatedLinesForPreview: Record<number, string> = {};

  /** Called by Viewer when text extraction finishes */
  onLinesExtracted(lineMap: Record<number, string>) {
    console.log('Received extracted line map:', lineMap);

    this.resumeDraft = {
      lines: Object.entries(lineMap).map(([id, text]) => ({
        lineId: Number(id),
        text,
        editedText: null
      }))
    };

    this.rebuildPreviewLines();

    if (this.evaluation) {
      this.attachLineIdsToSuggestions(this.evaluation);
    }
  }

  /** Called when UploadComponent finishes processing */
  onProcessed(data: { pdfUrl: string; evaluation: ResumeEvaluationResult }) {
    this.pdfSrc = data.pdfUrl;
    this.evaluation = data.evaluation;

    this.attachLineIdsToSuggestions(this.evaluation);
  }

  /** Attach best matching lineId to each suggestion */
  private attachLineIdsToSuggestions(evaluation: ResumeEvaluationResult) {
    if (!this.resumeDraft) return;

    for (const suggestion of evaluation.line_by_line_suggestions) {
      suggestion.lineId = this.findBestMatchingLineId(
        suggestion.original_text
      );
    }
  }

  /** Fuzzy match backend text → parsed resume line */
  private findBestMatchingLineId(originalText: string): number | null {
    if (!this.resumeDraft) return null;

    const target = originalText.toLowerCase().trim();
    let bestScore = 0;
    let bestId: number | null = null;

    for (const line of this.resumeDraft.lines) {
      const candidate = line.text.toLowerCase().trim();
      const score = this.wordOverlapScore(target, candidate);

      if (score > bestScore) {
        bestScore = score;
        bestId = line.lineId;
      }
    }

    return bestId;
  }

  private wordOverlapScore(a: string, b: string): number {
    const setA = new Set(a.split(/\s+/));
    const setB = new Set(b.split(/\s+/));
    let overlap = 0;

    for (const word of setA) {
      if (setB.has(word)) overlap++;
    }

    return overlap;
  }

  /** Apply suggestion → update draft */
  onApplySuggestion(update: { original: string; updated: string }) {
    if (!this.evaluation || !this.resumeDraft) return;

    const suggestion = this.evaluation.line_by_line_suggestions.find(
      s => s.original_text === update.original
    );

    if (!suggestion || suggestion.lineId == null) {
      console.warn('No matching lineId for suggestion:', update.original);
      return;
    }

    suggestion.edited_suggestion = update.updated;

    const draftLine = this.resumeDraft.lines.find(
      l => l.lineId === suggestion.lineId
    );

    if (!draftLine) {
      return;
    }

    // 🔹 APPLY
    if (update.updated !== suggestion.original_text) {
      suggestion.edited_suggestion = update.updated;
      draftLine.editedText = update.updated;
    }
    // 🔹 DISCARD
    else {
      suggestion.edited_suggestion = undefined;
      draftLine.editedText = null;
    }

    this.rebuildPreviewLines();
  }

  private rebuildPreviewLines() {
    if (!this.resumeDraft) return;

    this.originalLinesForPreview = {};
    this.updatedLinesForPreview = {};

    for (const line of this.resumeDraft.lines) {
      this.originalLinesForPreview[line.lineId] = line.text;
      if (line.editedText) {
        this.updatedLinesForPreview[line.lineId] = line.editedText;
      }
    }
  }

  /** Call this whenever resumeDraft changes or a suggestion is applied */
  updateResumeDraft(updatedLines: Record<number, string>) {
    if (!this.resumeDraft) return;

    for (const line of this.resumeDraft.lines) {
      line.editedText = updatedLines[line.lineId] ?? null;
    }

    // Rebuild preview mappings for binding
    this.rebuildPreviewLines();
  }
}
