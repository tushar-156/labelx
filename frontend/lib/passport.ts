import { useProfile } from "../store/profile";
import { useShelfStore } from "../store/shelf";

export interface Passport {
  label_passport: 1;
  exported: string;
  profile: {
    skinType: string;
    allergies: string;
    routine: string;
    season: string | null;
  };
  shelfCount: number;
}

export function buildPassport(): Passport {
  const profile = useProfile.getState();
  const shelf = useShelfStore.getState();

  return {
    label_passport: 1,
    exported: new Date().toISOString().slice(0, 10),
    profile: {
      skinType: profile.skinType,
      allergies: profile.allergies,
      routine: profile.routine,
      season: profile.season,
    },
    shelfCount: shelf.products.length,
  };
}

export function passportFilename(): string {
  return `label-passport-${new Date().toISOString().slice(0, 10)}.json`;
}

export function downloadPassport(): boolean {
  try {
    const blob = new Blob([JSON.stringify(buildPassport(), null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = passportFilename();
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 3000);
    return true;
  } catch {
    return false;
  }
}

export function importPassport(file: File): Promise<string | null> {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onerror = () => resolve(null);
    reader.onload = () => {
      try {
        const raw = JSON.parse(String(reader.result)) as Partial<Passport>;
        if (raw?.label_passport !== 1) {
          resolve("Not a valid Label passport.");
          return;
        }

        const p = raw.profile;
        if (p) {
          useProfile.getState().importProfile({
            skinType: p.skinType,
            allergies: p.allergies,
            routine: p.routine,
            season: p.season,
          });
        }
        resolve("Passport imported successfully!");
      } catch {
        resolve("Failed to parse passport file.");
      }
    };
    reader.readAsText(file);
  });
}
