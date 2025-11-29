import { Injectable } from '@angular/core';
import { ResumeEvaluationResult, LineSuggestion, SkillsMatch } from '../model/resume-evaluation-result.model';

@Injectable({
  providedIn: 'root',
})
export class ResumeService {

  constructor() {}

  /**
   * Simulate processing a resume against a job description.
   * Returns a mock PDF blob and dummy evaluation.
   */
  async processResume(
    file: File,
    payload: { job_text?: string; job_url?: string }
  ): Promise<{ pdfBlob: Blob; evaluation: ResumeEvaluationResult }> {

    // Simulate a delay
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Dummy evaluation
    const evaluation: ResumeEvaluationResult = {
      ats_score: 85,
      summary: 'Good fit overall. Some skills missing.',
      missing_keywords: ['CI/CD', 'Kubernetes'],
      skills_match: {
        matched_skills: ['APIs', 'JavaScript'],
        unmatched_skills: ['CI/CD', 'Kubernetes'],
      },
      section_feedback: [],
      line_by_line_suggestions: [
        {
          original_text: 'Worked on API integration.',
          suggested_improvement: 'Designed and implemented RESTful API integrations with 5+ microservices.',
          reason: 'Adds measurable impact and specificity.',
          edited_suggestion: '', // editable by user
        } as LineSuggestion,
      ],
      recommended_new_bullets: [],
    };

    // Create a dummy PDF blob (empty PDF)
    const pdfBlob = new Blob([new Uint8Array([37, 80, 68, 70, 45, 49, 46, 52, 10])], { type: 'application/pdf' });

    return { pdfBlob, evaluation };
  }

  /**
   * Simulate regenerating the resume PDF after applying suggestions
   */
  async regenerateResume(evaluation: ResumeEvaluationResult): Promise<string> {
    // Simulate backend PDF generation delay
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // For now, just return a new dummy blob URL
    const pdfBlob = new Blob([new Uint8Array([37, 80, 68, 70, 45, 49, 46, 52, 10])], { type: 'application/pdf' });
    return URL.createObjectURL(pdfBlob);
  }
}
