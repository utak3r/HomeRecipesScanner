import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { Recipe } from '../types/recipe';
import { ChefHat, Plus } from 'lucide-react';

export const RecipeList = () => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/recipes/').then(res => {
      setRecipes(res.data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 border-4 border-accent/30 border-t-accent rounded-full animate-spin" />
        <p className="text-gray-500 font-medium">Pobieranie przepisów...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex items-center justify-between mb-12">
        <div>
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Twoja Baza Przepisów</h1>
          <p className="text-gray-500 mt-2">Przeglądaj i inspiruj się do gotowania.</p>
        </div>
        <Link
          to="/add"
          className="inline-flex items-center px-6 py-3 rounded-xl font-medium text-white bg-accent hover:bg-accent/90 transition-colors shadow-sm shadow-accent/30"
        >
          <Plus className="w-5 h-5 mr-2" />
          Dodaj nowy przepis
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
        {recipes.map((recipe) => (
          <Link 
            key={recipe.id} 
            to={`/recipe/${recipe.id}`}
            className="group flex flex-col bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-lift transition-all duration-300 border border-gray-100 hover:-translate-y-1"
          >
            {/* Image Container */}
            <div className="relative aspect-[4/3] overflow-hidden bg-brand-50">
              {recipe.thumbnail_url ? (
                <img
                  src={`${api.defaults.baseURL}${recipe.thumbnail_url}`}
                  alt={recipe.title || "Przepis"}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-brand-100 text-brand-300">
                  <ChefHat size={48} />
                </div>
              )}
              {/* Overlay gradient */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </div>

            {/* Content */}
            <div className="p-6 flex flex-col flex-grow">
              <h2 className="text-xl font-bold text-gray-900 leading-tight mb-3 group-hover:text-accent transition-colors line-clamp-2">
                {recipe.title || "Przepis bez tytułu"}
              </h2>
              <p className="text-sm text-gray-500 line-clamp-3 mb-4 flex-grow">
                {recipe.short_text || "Brak krótkiego opisu."}
              </p>
              
              <div className="mt-auto pt-4 border-t border-gray-100 flex items-center text-sm font-medium text-accent">
                ZOBACZ PRZEPIS <span className="ml-2 transform group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};
