import { useEffect, useState } from 'react';
import axios from 'axios';
import { Recipe } from '../types/recipe';

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
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4">
      {recipes.map(recipe => (
        <div key={recipe.id} className="border rounded-lg overflow-hidden shadow-lg">
          <img
            src={`${API_BASE}${recipe.thumbnail_url}`}
            alt={recipe.title}
            className="w-full h-48 object-cover"
          />
          <div className="p-4">
            <h2 className="font-bold text-xl">{recipe.title || "Bez tytułu"}</h2>
            <p className="text-gray-600 text-sm mt-2">{recipe.short_text}</p>
          </div>
        </div>
      ))}
    </div>
  );
};
