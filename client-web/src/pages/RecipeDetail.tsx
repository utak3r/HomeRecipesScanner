import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { Recipe } from '../types/recipe';
import { ArrowLeft, ChefHat, Info, Maximize2 } from 'lucide-react';

export const RecipeDetail = () => {
  const { id } = useParams();
  const [recipe, setRecipe] = useState<Recipe | null>(null);

  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  useEffect(() => {
    api.get(`/recipes/${id}`).then(res => setRecipe(res.data));
  }, [id]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSelectedImage(null);
    };
    if (selectedImage) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden'; // Prevent scrolling when modal is open
    } else {
      document.body.style.overflow = 'auto';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'auto';
    };
  }, [selectedImage]);

  if (!recipe) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-6">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 border-4 border-accent/20 rounded-full"></div>
          <div className="absolute inset-0 border-4 border-accent border-t-transparent rounded-full animate-spin"></div>
        </div>
        <p className="text-gray-400 font-medium tracking-wide uppercase text-sm">Wczytywanie przepisu...</p>
      </div>
    );
  }

  const s = recipe.structured;

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-24">
      {/* Premium Hero Header */}
      <div className="relative w-full bg-white border-b border-gray-100 pt-12 pb-20">
        <div className="absolute inset-0 bg-gradient-to-b from-brand-50/50 to-transparent"></div>
        
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <Link 
            to="/" 
            className="inline-flex items-center text-sm text-gray-400 hover:text-accent font-semibold tracking-wide uppercase mb-12 transition-colors group"
          >
            <ArrowLeft className="w-4 h-4 mr-2 transform group-hover:-translate-x-1 transition-transform" />
            Wróć do przepisów
          </Link>

          <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
            <div className="max-w-3xl">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-brand-100 text-accent mb-6">
                <ChefHat size={24} />
              </div>
              <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 tracking-tight leading-[1.1] mb-6">
                {recipe.title || s?.title || "Przepis bez tytułu"}
              </h1>
              {recipe.short_text && (
                <p className="text-xl text-gray-500 font-light leading-relaxed max-w-2xl">
                  {recipe.short_text}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-20">
        <div className="grid lg:grid-cols-12 gap-8 lg:gap-12">
          
          {/* Ingredients Sidebar */}
          <div className="lg:col-span-5 xl:col-span-4">
            <div className="bg-white rounded-[2rem] p-8 shadow-sm border border-gray-100 sticky top-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-8 pl-4">
                Składniki
              </h2>
              <ul className="space-y-6">
                {s?.ingredients?.map((ing, idx) => (
                  <li key={idx} className="flex items-start group">
                    <div className="flex-shrink-0 w-2.5 h-2.5 rounded-full bg-brand-200 mt-2.5 mr-5"></div>
                    <div className="flex-grow flex flex-col sm:flex-row sm:items-start justify-between gap-1 sm:gap-4">
                      <span className="text-gray-700 font-medium text-lg leading-tight pt-1">
                        {ing.name}
                      </span>
                      <span className="text-accent font-bold text-lg sm:text-right w-full sm:max-w-[50%] break-words">
                        {ing.amount}
                      </span>
                    </div>
                  </li>
                ))}
                {(!s?.ingredients || s.ingredients.length === 0) && (
                  <li className="text-gray-400 font-light italic pl-7">Brak listy składników.</li>
                )}
              </ul>
            </div>
          </div>

          {/* Preparation Steps */}
          <div className="lg:col-span-7 xl:col-span-8 space-y-8">
            <div className="bg-white rounded-[2rem] p-8 md:p-10 shadow-sm border border-gray-100">
              <div className="space-y-12">
                {s?.steps?.map((step, idx) => (
                  <div key={idx} className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 group">
                    <div className="flex-grow sm:pr-8">
                      <p className="text-gray-800 leading-relaxed text-lg font-medium">
                        {step}
                      </p>
                    </div>
                    {/* Step Number on the Right (V2 Layout) */}
                    <div className="flex-shrink-0 self-end sm:self-center">
                      <div className="w-[4.5rem] h-[4.5rem] rounded-[1.5rem] bg-brand-50 border border-brand-100 text-brand-800 flex items-center justify-center font-extrabold text-3xl shadow-sm">
                        {idx + 1}
                      </div>
                    </div>
                  </div>
                ))}
                {(!s?.steps || s.steps.length === 0) && (
                  <p className="text-gray-400 font-light italic text-lg">Instrukcje nie zostały podane.</p>
                )}
              </div>
            </div>

            {/* Author Notes Card */}
            {s?.notes && (
              <div className="bg-gradient-to-br from-brand-50 to-white rounded-3xl p-8 border border-brand-100 relative overflow-hidden shadow-sm">
                <div className="absolute top-0 right-0 p-6 text-brand-200 opacity-30">
                  <Info size={100} />
                </div>
                <div className="relative z-10">
                  <h3 className="text-sm font-bold text-accent uppercase tracking-widest mb-4">
                    Wskazówki autora
                  </h3>
                  <p className="text-gray-800 text-lg font-light italic leading-relaxed max-w-2xl">
                    "{s.notes}"
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Gallery / Scans */}
        {recipe.images && recipe.images.length > 0 && (
          <div className="mt-16">
            <h2 className="text-2xl font-bold text-gray-900 mb-8 flex items-center justify-center">
              Oryginalne Skany
            </h2>
            <div className="flex flex-wrap justify-center gap-8">
              {recipe.images.map((img) => (
                <div key={img.id} className="w-full max-w-[500px]">
                  <button 
                    onClick={() => setSelectedImage(`${api.defaults.baseURL}${img.url}`)}
                    className="group block w-full relative rounded-[2rem] overflow-hidden bg-white p-3 shadow-soft hover:shadow-lift transition-all duration-500 border border-gray-100 cursor-zoom-in text-left focus:outline-none focus:ring-4 focus:ring-accent/20"
                  >
                    <div className="relative rounded-[1.5rem] overflow-hidden aspect-[3/4]">
                      <img
                        src={`${api.defaults.baseURL}${img.url}`}
                        className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                        alt="Skan przepisu"
                      />
                      {/* Hover Overlay */}
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                        <div className="bg-white/20 backdrop-blur-md rounded-full p-4 transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
                          <Maximize2 className="w-8 h-8 text-white" />
                        </div>
                      </div>
                    </div>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Image Lightbox Overlay */}
      {selectedImage && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4 md:p-8 backdrop-blur-sm transition-opacity"
          onClick={() => setSelectedImage(null)}
        >
          {/* Close button that is clearly visible */}
          <button 
            className="absolute top-6 right-6 md:top-10 md:right-10 w-12 h-12 flex items-center justify-center bg-white/10 hover:bg-white/20 text-white rounded-full transition-colors backdrop-blur-md"
            onClick={(e) => {
              e.stopPropagation();
              setSelectedImage(null);
            }}
            aria-label="Zamknij"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
          
          <img 
            src={selectedImage} 
            alt="Powiększony skan przepisu" 
            className="w-auto h-auto max-w-full max-h-full object-contain rounded-lg shadow-2xl cursor-zoom-out"
            onClick={(e) => {
              // Allow clicking the image itself to close
              e.stopPropagation();
              setSelectedImage(null);
            }}
          />
        </div>
      )}
    </div>
  );
};
