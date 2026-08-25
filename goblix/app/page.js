import { getAllMovies } from '@/lib/movies';
import Navbar from '@/components/Navbar';
import HeroBanner from '@/components/HeroBanner';
import CategoryFilter from '@/components/CategoryFilter';
import MovieGrid from '@/components/MovieGrid';
import Footer from '@/components/Footer';

export const dynamic = 'force-dynamic';

export default function HomePage() {
  const movies = getAllMovies();
  const featured = movies.find(m => m.slug === 'top-gun-maverick') || movies[0];

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#141414]">
      <Navbar />
      
      {/* 100vh Edge-to-Edge Hero Banner */}
      <HeroBanner movie={featured} />

      {/* Main Content Area */}
      <main className="relative z-20 px-4 sm:px-8 md:px-12 -mt-16 sm:-mt-24 space-y-8 pb-16 flex-1">
        <CategoryFilter />
        <MovieGrid />
      </main>

      <Footer />
    </div>
  );
}
