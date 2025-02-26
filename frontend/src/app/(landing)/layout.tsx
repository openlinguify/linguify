import type { Metadata } from "next";
import { Navbar } from "./_components/Navbar";

export const metadata: Metadata = {
    title: "Linguify",
    description: "Landing page for Linguify",
  };

export default function Layout({
    children,
  }: Readonly<{
    children: React.ReactNode;
  }>) {
    return (
      <html lang="en" suppressHydrationWarning>
        <body>
          <>
            <Navbar />
            <div>{children}</div>
          </>
        </body>
      </html>
    );
  }