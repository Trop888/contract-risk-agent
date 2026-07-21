import { useState } from "react";

interface Props {
  loading: boolean;
  onAnalyze: (files: File[]) => void;
  onReset: () => void;
}

export default function UploadPanel({ loading, onAnalyze, onReset }: Props) {
  const [files, setFiles] = useState<File[]>([]);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <label className="mb-2 block text-sm font-medium text-slate-700">
        选择合同文件（可多选：多页照片、合同+附件会合并为一份分析）
      </label>
      <input
        type="file"
        multiple
        accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
            onChange={(e) => {
          setFiles(Array.from(e.target.files ?? []));
          onReset();
        }}
        className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:font-medium file:text-blue-700 hover:file:bg-blue-100"
      />
      {files.length > 0 && (
        <p className="mt-2 text-xs text-slate-500">已选择 {files.length} 个文件</p>
      )}
      <button
        disabled={files.length === 0 || loading}
        onClick={() => onAnalyze(files)}
        className="mt-4 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {loading ? "分析中..." : "🚀 开始分析"}
      </button>
    </div>
  );
}