import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/context/AuthContext';
import Navbar from '@/components/Navbar';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  weight: ['400', '500', '600', '700'],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains',
  weight: ['400', '500', '600'],
});

export const metadata = {
  title: 'Resume Gala — AI-Powered Portfolio Website Generator',
  description:
    'Transform your resume into a stunning portfolio website using AI-orchestrated multi-agent pipeline. Live preview, one-click deploy, and conversational editing.',
  keywords: ['resume', 'portfolio', 'AI', 'website generator', 'React'],
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body>
        <AuthProvider>
          <Navbar />
          <main className="page-wrapper">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
