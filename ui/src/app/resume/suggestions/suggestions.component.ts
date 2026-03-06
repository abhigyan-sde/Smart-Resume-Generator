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
    item.isApplied = true;
    item.edited_suggestion = item.suggested_improvement;

    this.suggestionApplied.emit({
      original: item.original_text,
      updated: item.edited_suggestion,
    });
  }

  discardSuggestion(item: LineSuggestion) {
    item.isApplied = false;
    item.edited_suggestion = item.original_text;

    this.suggestionApplied.emit({
      original: item.original_text,
      updated: item.original_text,
    });
  }

  removeSuggestion(item: LineSuggestion) {
    const idx = this.suggestions.indexOf(item);
    if (idx !== -1) 
      this.evaluation!.line_by_line_suggestions.splice(idx, 1);
  }
}
