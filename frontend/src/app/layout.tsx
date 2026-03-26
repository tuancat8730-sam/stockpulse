import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "StockPulse VN",
  description: "Bản tin chứng khoán Việt Nam qua Telegram",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
