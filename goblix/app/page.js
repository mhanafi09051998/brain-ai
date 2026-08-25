import { getAllMovies } from '@/lib/movies';
import Navbar from '@/components/Navbar';
import HeroBanner from '@/components/HeroBanner';
import MovieGrid from '@/components/MovieGrid';
import Footer from '@/components/Footer';

export const dynamic = 'force-dynamic';

export default function HomePage() {
  const movies = getAllMovies();
  const featured = movies.find(m => m.slug === 'top-gun-maverick') || movies[0];

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#141414]">
      <Navbar />
      
      {/* 100vh Full Viewport Edge-to-Edge Hero Backdrop */}
      {featured && <HeroBanner movie={featured} />}

      {/* Main Content Area - Starts Below Full Backdrop */}
      <main className="relative z-20 px-4 sm:px-8 md:px-12 py-10 space-y-8 flex-1 bg-[#141414]">
        <MovieGrid />
      </main>

      <Footer />
    </div>
  );
}
