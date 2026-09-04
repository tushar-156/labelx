import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: process.env.SITE_URL ? new URL(process.env.SITE_URL) : undefined,
  title: "LabelX — The AI Label Analyzer",
  description:
    "An AI-powered OCR and cross-referencing engine that instantly translates complex chemical labels into actionable safety profiles. Backed by clinical science.",
  keywords: [
    "cosmetics",
    "skincare",
    "safety",
    "ingredients",
    "OCR",
    "label analyzer",
    "INCI",
    "toxicology",
  ],
  authors: [{ name: "srivtx" }],
  openGraph: {
    title: "LabelX — The AI Label Analyzer",
    description:
      "Deterministic safety verdicts for skincare ingredients, drawn from clinical literature.",
    siteName: "LabelX",
    type: "website",
    images: [{ url: "/og-card.png", width: 1200, height: 630, alt: "LabelX — AI Skincare Analyzer" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "LabelX — The AI Label Analyzer",
    description:
      "Deterministic safety verdicts for skincare ingredients, drawn from clinical literature.",
    images: ["/og-card.png"],
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: dark)", color: "#050505" },
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
  ],
};

/* Applied before first paint so the saved theme never flashes: the
   night ledger is the default; "light" rides the document root. */
const THEME_BOOT = `(function(){try{var t=localStorage.getItem("LabelX-theme");if(t!=="dark")document.documentElement.classList.add("light")}catch(e){}})();`;

import { Providers } from "./providers";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_BOOT }} />
      </head>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
