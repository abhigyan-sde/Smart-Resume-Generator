import { Injectable } from '@angular/core';
import { ResumeEvaluationResult, LineSuggestion, SkillsMatch } from '../model/resume-evaluation-result.model';
import { ResumeGenerationPayLoad } from '../model/resume-parser.model';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class ResumeService {
  constructor(private http: HttpClient){}

  private API_URL = 'http://localhost:8000/resume';

  private getMockResponse() : ResumeEvaluationResult{
    return {
      ats_score: 75,
      summary:
        "The candidate has a strong background in software engineering with relevant experience in cloud technologies and machine learning. However, there are gaps in specific AI/ML techniques and programming languages required for the role.",
      missing_keywords: [
        "C++",
        "Generative AI",
        "Computer Vision",
        "Natural Language Processing",
        "Deep Learning",
        "Neural Networks",
        "statistical data analysis",
      ],
      skills_match: {
        matched_skills: [
          "Python",
          "Java",
          "AWS",
          "Machine Learning",
          "Data Processing",
          "Debugging",
          "Infrastructure-as-Code",
        ],
        unmatched_skills: [
          "C++",
          "Generative AI",
          "Computer Vision",
          "Natural Language Processing",
          "Deep Learning",
          "Neural Networks",
          "statistical data analysis",
        ],
      },
      section_feedback: [
        {
          section: "Technical Skills",
          issues: [
            "Missing C++ experience",
            "Lack of specific AI/ML techniques mentioned in the JD",
          ],
        },
        {
          section: "Work Experience",
          issues: [
            "No mention of experience with Generative AI or Computer Vision",
            "Limited focus on ML infrastructure and optimization",
          ],
        },
      ],
      line_by_line_suggestions: [
        {
          original_text:
            "• Reduced regression testing time by 50% by architecting a script less automation framework in Spring Boot that streamlined workflows and enabled faster release cycles.",
          suggested_improvement:
            "• Achieved a 50% reduction in regression testing time by architecting a scriptless automation framework in Spring Boot, significantly enhancing workflow efficiency and accelerating release cycles.",
          reason:
            "Improves clarity and emphasizes the impact of the achievement.",
        },
        {
          original_text:
            "• Designed and deployed data pipelines to capture testing KPIs, leveraging AWS QuickSight dashboards to guide leadership in cost optimization decisions.",
          suggested_improvement:
            "• Designed and deployed robust data pipelines to capture testing KPIs, utilizing AWS QuickSight dashboards to provide actionable insights for leadership on cost optimization strategies.",
          reason:
            "Enhances clarity and highlights the strategic impact of the work.",
        },
      ],
      recommended_new_bullets: [
        {
          job_responsibility_from_jd:
            "Implement solutions in one or more specialized Machine Learning (ML) areas.",
          suggested_bullet:
            "Developed and deployed machine learning models for predictive analytics, optimizing data processing workflows and enhancing decision-making capabilities.",
          importance: "high",
        },
        {
          job_responsibility_from_jd:
            "Contribute to model optimization and data processing.",
          suggested_bullet:
            "Collaborated on model optimization techniques, improving model performance by 30% through advanced data processing strategies.",
          importance: "high",
        },
        {
          job_responsibility_from_jd:
            "Experience with statistical data analysis.",
          suggested_bullet:
            "Applied statistical data analysis methods to evaluate model performance and derive insights from large datasets.",
          importance: "medium",
        },
      ],
    };
  }

  /**
   * Simulate processing a resume against a job description.
   * Returns a mock PDF blob and dummy evaluation.
   */
  async processResume(
    file: File,
    payload: { job_text?: string; job_url?: string }
  ): Promise<ResumeEvaluationResult> {
    const formData = new FormData();

    // Attach file
    formData.append('resume_file', file);

    // Attach optional fields
    if (payload.job_text) formData.append('job_text', payload.job_text);
    else if (payload.job_url) formData.append('job_url', payload.job_url);

    return this.getMockResponse();
    // Make API call
    // const response = await fetch(this.API_URL, {
    //   method: 'POST',
    //   body: formData,
    // });

    // if (!response.ok) {
    //   throw new Error(`API error: ${response.status}`);
    // }
    // const data = await response.json();
    // return data.evaluation as ResumeEvaluationResult;
  }

  private base64ToBlob(base64: string, mime: string): Blob {
    const byteChars = atob(base64);
    const byteNumbers = new Array(byteChars.length);

    for (let i = 0; i < byteChars.length; i++) {
      byteNumbers[i] = byteChars.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mime });
  }

  /**
   * Simulate regenerating the resume PDF after applying suggestions
   */
  generateResume(payload: ResumeGenerationPayLoad, file: File) {
    const formData = new FormData();
    formData.append('uploaded_file', file); 
    formData.append('payload', JSON.stringify(payload));
    return this.http.post(
      `${this.API_URL}/generate-resume`,
        formData,
      { responseType: 'blob' }
    );
  }
}
