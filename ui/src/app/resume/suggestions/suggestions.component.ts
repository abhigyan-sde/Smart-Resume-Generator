import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ResumeEvaluationResult, LineSuggestion } from '../model/resume-evaluation-result.model';

@Component({
  selector: 'app-suggestions-panel',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './suggestions.component.html',
  styleUrls: ['./suggestions.component.css'],
})
export class SuggestionsComponent {
  @Input() evaluation: ResumeEvaluationResult | null = null;
  @Output() suggestionApplied = new EventEmitter<{ original: string; updated: string }>();

  // helper getter to avoid *ngIf checks in template
  get suggestions(): LineSuggestion[] {
    return this.evaluation?.line_by_line_suggestions || [];
  }

  applySuggestion(item: LineSuggestion) {
    this.suggestionApplied.emit({
      original: item.original_text,
      updated: item.edited_suggestion || item.suggested_improvement,
    });
  }

  resetSuggestion(item: LineSuggestion) {
    item.edited_suggestion = item.suggested_improvement;
  }
}
