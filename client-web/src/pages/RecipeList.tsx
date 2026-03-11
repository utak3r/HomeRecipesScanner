import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { Recipe } from '../types/recipe';

export const RecipeList = () => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/recipes/').then(res => {
      setRecipes(res.data);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="p-10 text-center text-gray-500">Pobieranie listy przepisów...</div>;

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20">Miniatura</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tytuł</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Skrót treści</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Akcje</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {recipes.map((recipe, idx) => (
            <tr key={recipe.id} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50 hover:bg-orange-50 transition-colors'}>
              <td className="px-6 py-4 whitespace-nowrap">
                <img
                  src={`${api.defaults.baseURL}${recipe.thumbnail_url}`}
                  alt=""
                  className="h-12 w-12 rounded object-cover border border-gray-200"
                />
              </td>
              <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                {recipe.title || "Bez tytułu"}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500 max-w-md truncate">
                {recipe.short_text}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <Link to={`/recipe/${recipe.id}`} className="text-orange-600 hover:text-orange-900">
                  Otwórz →
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
