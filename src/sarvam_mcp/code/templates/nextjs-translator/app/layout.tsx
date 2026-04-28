import type { Metadata, Viewport } from "next";

export const metadata: Metadata = {
  title: "${PROJECT_NAME}",
  description: "Indic translator powered by Sarvam Mayura v1.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, background: "#fafafa" }}>{children}</body>
    </html>
  );
}
