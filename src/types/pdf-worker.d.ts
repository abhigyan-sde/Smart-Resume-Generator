// tell TypeScript how to handle imports ending with ?worker
declare module 'pdfjs-dist/build/pdf.worker.min.mjs?worker' {
  const workerConstructor: new () => Worker;
  export default workerConstructor;
}
