import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { Recipe } from '../types/recipe';
import { ChefHat } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const RecipeList = () => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);

  useEffect(() => {
    const fetchRecipes = async () => {
      const response = await axios.get(`${API_BASE}/recipes/`);
      setRecipes(response.data);
    };
    fetchRecipes();
  }, []);

  return (
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
                src={`${API_BASE}${recipe.thumbnail_url}`}
                alt={recipe.title || "Przepis"}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-brand-100 text-brand-300">
                <ChefHat size={48} />
              </div>
            )}
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
  );
};
