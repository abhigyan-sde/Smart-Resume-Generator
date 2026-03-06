import { Component, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ResumeEvaluationResult } from '../model/resume-evaluation-result.model';
import { ResumeService } from '../service/resume.service';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatRadioModule } from '@angular/material/radio';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDividerModule } from '@angular/material/divider';

@Component({
  selector: 'app-resume-upload',
  standalone: true,
  imports: [
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatRadioModule,
    MatFormFieldModule,
    MatInputModule,
    MatDividerModule,
  ],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css'],
})
export class UploadComponent {
  resumeFile: File | null = null;
  resumeFileName: string | null = null;
  resumePreviewUrl: SafeResourceUrl | null = null; // Instant preview
  pdfUrl: string | undefined;
  jobUrl: string = '';
  jobDescription: string = '';
  inputMode: 'url' | 'description' = 'url';
  loading: boolean = false;

  @Output() processed = new EventEmitter<{ pdfUrl: string; evaluation: ResumeEvaluationResult }>();

  constructor(private resumeService: ResumeService, private sanitizer: DomSanitizer) {}

  /** When user selects a file, set it and generate preview immediately */
  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.resumeFile = file;
      this.resumeFileName = file.name;

      // Generate instant PDF preview
      this.pdfUrl = URL.createObjectURL(file);
      this.processed.emit({ pdfUrl: this.pdfUrl, evaluation: null! });
    }
  }

  /** Toggle input mode between Job URL and Job Description */
  setMode(mode: 'url' | 'description') {
    this.inputMode = mode;
  }

  /** Submit the resume to backend for evaluation */
  async submit() {
    if (!this.resumeFile) return;

    const payload: { job_text?: string; job_url?: string } = {};
    if (this.inputMode === 'url' && this.jobUrl) payload.job_url = this.jobUrl;
    if (this.inputMode === 'description' && this.jobDescription) payload.job_text = this.jobDescription;

    if (!payload.job_text && !payload.job_url) 
      return;

    this.loading = true;

    try {
      const result = await this.resumeService.processResume(this.resumeFile, payload);
      // Emit backend-processed evaluation
      this.processed.emit({pdfUrl: this.pdfUrl!, evaluation: result });
    } catch (error) {
      console.error('Error processing resume:', error);
    } finally {
      this.loading = false;
    }
  }
}