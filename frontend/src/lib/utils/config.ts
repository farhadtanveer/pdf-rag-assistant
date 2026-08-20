export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  pdfWorkerSrc: new URL(
    "pdfjs-dist/build/pdf.worker.min.js",
    import.meta.url
  ).toString(),
}
