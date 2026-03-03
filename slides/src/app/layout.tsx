import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";

const geist = Geist({
    variable: "--font-geist-sans",
    subsets: ["latin"],
});

export const metadata: Metadata = {
    title: "BiDAF QA — NLP Presentation",
    description: "Closed-Domain Question Answering with BiDAF on SQuAD 2.0",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={`${geist.variable} antialiased`}>
                {children}
            </body>
        </html>
    );
}
