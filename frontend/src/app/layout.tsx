import './globals.css';
import type { ReactNode } from 'react';

export const metadata = {
  title: 'OpenLLM',
  description: 'Private coding assistant',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
