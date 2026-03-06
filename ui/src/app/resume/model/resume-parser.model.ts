export interface PhysicalSegment {
  page: number;
  y: number;
  xStart: number;
  xEnd: number;
  rawText: string;
}

export interface LogicalLine {
  lineId: number;
  text: string;
  segments: PhysicalSegment[];
}

export interface ResumeDraft {

  lines: { lineId: number; text: string; editedText: string | null }[];
  logicalLines?: LogicalLine[];
  editedLines?: Record<number, string>;
}
