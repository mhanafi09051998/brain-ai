import './globals.css';
import { GoblixProvider } from '@/lib/store';
import { getAllMovies } from '@/lib/movies';
import MoviePreviewModal from '@/components/MoviePreviewModal';
import AuthModal from '@/components/AuthModal';
import MyListModal from '@/components/MyListModal';

export const metadata = {
  title: 'Goblix - Nonton Film 1080p BluRay Subtitle Indonesia',
  description: 'Platform Streaming Film 1080p BluRay Subtitle Indonesia Resmi Tanpa Iklan Pop-up.',
  manifest: '/manifest.json',
  icons: {
    icon: 'https://images.unsplash.com/photo-1578632767115-351597cf2477?w=192&auto=format&fit=crop&q=80'
  }
};

export default function RootLayout({ children }) {
  const initialMovies = getAllMovies();

  return (
    <html lang="id">
      <head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
        />
      </head>
      <body className="bg-[#141414] text-white min-h-screen flex flex-col antialiased">
        <GoblixProvider initialMovies={initialMovies}>
          <div className="flex-1 flex flex-col">
            {children}
          </div>
          <MoviePreviewModal />
          <AuthModal />
          <MyListModal />
        </GoblixProvider>
      </body>
    </html>
  );
}
