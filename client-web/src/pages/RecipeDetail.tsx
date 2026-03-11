import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { Recipe } from '../types/recipe';

export const RecipeDetail = () => {
  const { id } = useParams();
  const [recipe, setRecipe] = useState<Recipe | null>(null);

  useEffect(() => {
    api.get(`/recipes/${id}`).then(res => setRecipe(res.data));
  }, [id]);

  if (!recipe) return <div className="p-8 text-center text-gray-500">Ładowanie...</div>;

  const s = recipe.structured;

  return (
    <div className="max-w-4xl mx-auto bg-white shadow-lg rounded-xl overflow-hidden border border-gray-100">
      {/* Nagłówek */}
      <div className="bg-orange-50 p-6 border-b border-orange-100">
        <Link to="/" className="text-orange-600 text-sm font-semibold hover:underline mb-2 block">← Powrót do listy</Link>
        <h1 className="text-4xl font-extrabold text-gray-900">{recipe.title || s?.title || "Bez tytułu"}</h1>
      </div>

      <div className="p-8">
        <div className="grid md:grid-cols-3 gap-10">
          {/* Kolumna boczna: Składniki */}
          <div className="md:col-span-1">
            <h2 className="text-xl font-bold text-gray-800 mb-4 border-b-2 border-orange-200 pb-2">Składniki</h2>
            <ul className="space-y-3">
              {s?.ingredients?.map((ing, idx) => (
                <li key={idx} className="flex flex-col text-sm border-b border-gray-50 pb-2">
                  <span className="font-bold text-orange-700">{ing.amount}</span>
                  <span className="text-gray-700">{ing.name}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Kolumna główna: Kroki */}
          <div className="md:col-span-2">
            <h2 className="text-xl font-bold text-gray-800 mb-4 border-b-2 border-orange-200 pb-2">Przygotowanie</h2>
            <div className="space-y-6">
              {s?.steps?.map((step, idx) => (
                <div key={idx} className="flex gap-4">
                  <span className="flex-shrink-0 w-8 h-8 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center font-bold">
                    {idx + 1}
                  </span>
                  <p className="text-gray-700 leading-relaxed pt-1">{step}</p>
                </div>
              ))}
            </div>

            {s?.notes && (
              <div className="mt-10 p-5 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                <h3 className="font-bold text-blue-800 mb-1">Dodatkowe wskazówki</h3>
                <p className="text-blue-900 italic text-sm">{s.notes}</p>
              </div>
            )}
          </div>
        </div>

        {/* Sekcja zdjęć: Na samym dole */}
        {recipe.images && recipe.images.length > 0 && (
          <div className="mt-12 border-t pt-8">
            <h2 className="text-xl font-bold text-gray-800 mb-6">Oryginalne skany / zdjęcia</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {recipe.images.map((img) => (
                <a key={img.id} href={`${api.defaults.baseURL}${img.url}`} target="_blank" rel="noreferrer">
                  <img
                    src={`${api.defaults.baseURL}${img.url}`}
                    className="rounded-lg shadow hover:opacity-90 transition-opacity cursor-zoom-in w-full"
                    alt="Skan przepisu"
                  />
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
