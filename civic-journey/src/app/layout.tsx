import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { CivicProvider, CivicBadgeTracker } from "@/components/CivicRewardsContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CivicJourney: Interactive Election Guide",
  description: "Empowering you to navigate the electoral process with confidence and clarity.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#F8F9FA]">
        <CivicProvider>
          <header className="fixed top-0 left-0 right-0 z-40 bg-white/80 backdrop-blur-md border-b border-gray-100 h-16 flex items-center justify-between px-4 sm:px-8 shadow-sm">
            <div className="font-bold text-[#005A9C] text-xl tracking-tight">CivicJourney</div>
            <CivicBadgeTracker />
          </header>
          <main className="flex-1 pt-16">
            {children}
          </main>
        </CivicProvider>
      </body>
    </html>
  );
}
