import { useRef, useState } from "react";
import { downloadPassport, importPassport } from "../../lib/passport";
import { Download, Upload, Share } from "lucide-react";
import { useProfile } from "../../store/profile";

export function PassportCard() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const { skinType, allergies, routine, season } = useProfile();

  const onImport = async (file: File | undefined) => {
    if (!file || busy) return;
    setBusy(true);
    const result = await importPassport(file);
    setBusy(false);
    alert(result);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className="rounded-[8px] border border-line2 bg-card p-4">
      <div className="flex items-center gap-2 mb-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-ink text-paper">
          <Download size={16} />
        </div>
        <div>
          <h3 className="text-[14px] font-semibold text-ink leading-tight">Beauty Passport</h3>
          <p className="text-[11px] text-inksoft">Your profile is yours — export it or back it up</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5 mb-4">
        {season && <span className="rounded-full bg-paper2 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-ink">{season}</span>}
        {skinType && <span className="rounded-full bg-paper2 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-ink">{skinType} skin</span>}
        {allergies && <span className="rounded-full bg-rose/10 text-rose px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider">allergies</span>}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="application/json,.json"
        className="hidden"
        onChange={(e) => onImport(e.target.files?.[0])}
      />

      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={() => {
            const ok = downloadPassport();
            alert(ok ? "Passport saved!" : "Couldn't save the file.");
          }}
          className="flex h-9 items-center justify-center gap-1.5 rounded-[4px] border border-line2 bg-paper text-[12px] font-medium text-ink hover:bg-paper2 transition-colors"
        >
          <Download size={14} /> Export
        </button>
        <button
          onClick={() => inputRef.current?.click()}
          className="flex h-9 items-center justify-center gap-1.5 rounded-[4px] bg-ink text-[12px] font-medium text-paper hover:bg-ink/90 transition-colors"
        >
          <Upload size={14} /> Import
        </button>
      </div>
    </div>
  );
}
