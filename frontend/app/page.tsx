"use client";

import { useState } from "react";
import axios from "axios";

type FileWithPreview = {
  file: File;
  preview: string;
};

export default function Home() {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleDrop = (e: any) => {
    e.preventDefault();

    const dropped = Array.from(e.dataTransfer.files) as File[];

    const newFiles = dropped.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
    }));

    setFiles((prev) => [...prev, ...newFiles]);
  };

  const handleUpload = async () => {
    if (!files.length) return;

    const formData = new FormData();

    files.forEach((f) => {
      formData.append("files", f.file);
    });

    setLoading(true);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/classify",
        formData
      );

      setResults(res.data.results);
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg, #0f172a, #1e293b, #4c1d95)",
        color: "white",
        padding: "40px",
      }}
    >
      <h1 style={{ textAlign: "center", fontSize: "32px" }}>
        Document Classifier
      </h1>

      {/* Drop Area */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        style={{
          border: "2px dashed #6b7280",
          borderRadius: "16px",
          padding: "30px",
          marginTop: "30px",
          textAlign: "center",
          backgroundColor: "#020617",
        }}
      >
        <label
  style={{
    padding: "10px 20px",
    backgroundColor: "#ec4899",
    borderRadius: "999px",
    color: "white",
    cursor: "pointer",
    fontWeight: "600",
    display: "inline-block",
  }}
>
  Upload Image
  <input
    type="file"
    multiple
    accept="image/*"
    style={{ display: "none" }}
    onChange={(e) => {
      const selectedFiles = Array.from(e.target.files || []);

      const newFiles = selectedFiles.map((file) => ({
        file,
        preview: URL.createObjectURL(file),
      }));

      setFiles((prev) => [...prev, ...newFiles]);
    }}
  />
</label>

        <p style={{ marginTop: "10px", color: "#9ca3af" }}>
          or drag & drop files here
        </p>

        {/* Preview Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))",
            gap: "15px",
            marginTop: "20px",
          }}
        >
          {files.map((f, i) => (
            <div
              key={i}
              style={{
                background: "#111827",
                padding: "10px",
                borderRadius: "10px",
              }}
            >
              <img
                src={f.preview}
                alt="preview"
                style={{
                  width: "100%",
                  height: "100px",
                  objectFit: "cover",
                  borderRadius: "8px",
                }}
              />
              <p
                style={{
                  fontSize: "12px",
                  marginTop: "5px",
                  wordBreak: "break-word",
                }}
              >
                {f.file.name}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Upload Button */}
      <div style={{ textAlign: "center", marginTop: "20px" }}>
        <button
          onClick={handleUpload}
          disabled={loading}
          style={{
            padding: "12px 30px",
            backgroundColor: "#ec4899",
            borderRadius: "999px",
            border: "none",
            color: "white",
            cursor: "pointer",
            fontWeight: "600",
            fontSize: "16px",
          }}
        >
          {loading ? "Classifying..." : "Classify Images"}
        </button>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div style={{ marginTop: "40px" }}>
          <h2 style={{ marginBottom: "20px" }}>Results</h2>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
              gap: "20px",
            }}
          >
            {results.map((r, i) => {
              const matchedFile = files.find(
                (f) => f.file.name === r.file
              );

              return (
                <div
                  key={i}
                  style={{
                    background: "#020617",
                    padding: "15px",
                    borderRadius: "12px",
                  }}
                >
                  {matchedFile && (
                    <img
                      src={matchedFile.preview}
                      alt="result"
                      style={{
                        width: "100%",
                        height: "120px",
                        objectFit: "cover",
                        borderRadius: "8px",
                      }}
                    />
                  )}

                  <p style={{ marginTop: "10px", fontSize: "14px" }}>
                    <strong>{r.file}</strong>
                  </p>

                  <p style={{ color: "#22c55e", marginTop: "5px" }}>
                    {r.category}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}