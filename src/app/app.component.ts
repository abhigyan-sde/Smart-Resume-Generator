import { Component } from '@angular/core';
import { UploadComponent } from './resume/upload/upload.component';
import { ViewerComponent } from './resume/viewer/viewer.component';
import { SuggestionsComponent } from './resume/suggestions/suggestions.component';
import { ResumeEvaluationResult } from './resume/model/resume-evaluation-result.model';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatRadioModule } from '@angular/material/radio';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDividerModule } from '@angular/material/divider';
import { MatToolbar } from '@angular/material/toolbar';
import { SafeResourceUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-root',
  imports: [UploadComponent, ViewerComponent, 
    SuggestionsComponent,FormsModule,MatCardModule,
    MatToolbar,
    MatButtonModule,
    MatRadioModule,
    MatFormFieldModule,
    MatInputModule,
    MatDividerModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'smart_resume_ui';

  pdfSrc: string | null = null;

  /** Full AI evaluation result passed to suggestions panel */
  evaluation: ResumeEvaluationResult | null = null;

  /** Called when UploadComponent finishes processing */
  onProcessed(data: { pdfUrl: string; evaluation: ResumeEvaluationResult }) {
    this.pdfSrc = data.pdfUrl;
    this.evaluation = data.evaluation;
  }

  /** When user clicks "Apply suggestion" */
  onApplySuggestion(update: { original: string; updated: string }) {
     if (!this.evaluation) return;

    console.log("Apply suggestion:", update);

// 1️⃣ Update in-memory line suggestion
    const line = this.evaluation.line_by_line_suggestions.find(
      (item) => item.original_text === update.original
    );
    if (line) {
      line.edited_suggestion = update.updated;
    }

    try {
      this.pdfSrc = null; // reset viewer while regenerating
      // const updatedPdfUrl = await this.resumeService.regenerateResume(
      //   this.evaluation
      // );

      //this.pdfSrc = updatedPdfUrl;
    } catch (error) {
      console.error('Failed to regenerate PDF:', error);
    }
  }
}
