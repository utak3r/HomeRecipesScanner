import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { Recipe } from '../types/recipe';
import { ChefHat, Plus, AlertTriangle, RefreshCw, Tag as TagIcon, Settings2, Search, X } from 'lucide-react';
import { useAuth } from '../components/AuthContext';
import { TagManagerModal } from '../components/TagManagerModal';

export const RecipeList = () => {
  const { isAuthenticated } = useAuth();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [allTags, setAllTags] = useState<{id: number, name: string}[]>([]);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [showTagManager, setShowTagManager] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 400);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch all tags for the filter
  const fetchTags = () => {
    if (isAuthenticated) {
      api.get('/tags/')
        .then(res => setAllTags(res.data))
        .catch(err => console.error('Failed to fetch tags:', err));
    }
  };

  useEffect(() => {
    fetchTags();
  }, [isAuthenticated]);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    
    let endpoint = '/recipes/';
    
    if (debouncedSearchQuery.trim()) {
      endpoint = `/recipes/search/?q=${encodeURIComponent(debouncedSearchQuery.trim())}`;
    } else if (selectedTag) {
      endpoint = `/recipes/by-tag/${encodeURIComponent(selectedTag)}`;
    }

    api.get(endpoint)
      .then(res => {
        if (isMounted) {
          setRecipes(res.data);
          setLoading(false);
        }
      })
      .catch(err => {
        console.error('Failed to fetch recipes:', err);
        if (isMounted) {
          setLoading(false);
        }
      });
    return () => { isMounted = false; };
  }, [isAuthenticated, selectedTag, debouncedSearchQuery]);

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
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-12 gap-6">
        <div>
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Twoja Baza Przepisów</h1>
          <p className="text-gray-500 mt-2">Przeglądaj i inspiruj się do gotowania.</p>
        </div>
        
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          {/* Search Field */}
          <div className="relative group min-w-[280px]">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 group-focus-within:text-accent transition-colors" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                if (e.target.value.trim() && selectedTag) {
                  setSelectedTag(null);
                }
              }}
              placeholder="Szukaj przepisu..."
              className="w-full pl-11 pr-11 py-3 bg-white border border-gray-200 rounded-2xl focus:outline-none focus:ring-4 focus:ring-accent/10 focus:border-accent transition-all shadow-sm"
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 rounded-full text-gray-400 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <button
            onClick={() => setShowTagManager(true)}
            className="flex items-center justify-center gap-2 px-5 py-3 bg-white border border-gray-200 text-gray-700 rounded-2xl font-bold hover:bg-gray-50 transition-all shadow-sm"
          >
            <Settings2 className="w-5 h-5" />
            <span className="hidden sm:inline">Tagi</span>
          </button>
          
          <Link 
            to="/add" 
            className="flex items-center justify-center gap-2 px-6 py-3 bg-accent text-white rounded-2xl font-bold hover:bg-accent/90 transition-all shadow-sm shadow-accent/30"
          >
            <Plus className="w-5 h-5" />
            <span className="hidden sm:inline">Dodaj nowy przepis</span>
          </Link>
        </div>
      </div>

      {isAuthenticated && (
        <div className="mb-10 flex items-center gap-3 overflow-x-auto pb-4 no-scrollbar">
          <button 
            onClick={() => setSelectedTag(null)}
            className={`px-5 py-2.5 rounded-full text-sm font-semibold transition-all whitespace-nowrap ${
              selectedTag === null 
                ? 'bg-accent text-white shadow-md shadow-accent/20' 
                : 'bg-white text-gray-600 border border-gray-100 hover:border-accent/30'
            }`}
          >
            Wszystkie
          </button>
          {allTags.map(tag => (
            <button
              key={tag.id}
            onClick={() => {
              setSelectedTag(tag.name);
              setSearchQuery('');
            }}
              className={`px-5 py-2.5 rounded-full text-sm font-semibold transition-all whitespace-nowrap flex items-center ${
                selectedTag === tag.name
                  ? 'bg-accent text-white shadow-md shadow-accent/20'
                  : 'bg-white text-gray-600 border border-gray-100 hover:border-accent/30'
              }`}
            >
              <TagIcon size={14} className="mr-2 opacity-70" />
              {tag.name}
            </button>
          ))}
        </div>
      )}

      {!isAuthenticated ? (
        <div className="bg-white rounded-[2rem] p-12 text-center border border-gray-100 shadow-sm">
          <div className="w-20 h-20 bg-brand-50 text-brand-300 rounded-full flex items-center justify-center mx-auto mb-6">
            <ChefHat size={40} />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Witaj w Bazie Przepisów!</h2>
          <p className="text-gray-500 max-w-md mx-auto mb-8">
            Zaloguj się, aby przeglądać swoje przepisy, skanować nowe i tworzyć własną kolekcję kulinarną.
          </p>
        </div>
      ) : recipes.length === 0 ? (
        <div className="bg-white rounded-[2rem] p-12 text-center border border-gray-100 shadow-sm">
          <div className="w-20 h-20 bg-brand-50 text-brand-300 rounded-full flex items-center justify-center mx-auto mb-6">
            <ChefHat size={40} />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Brak przepisów</h2>
          <p className="text-gray-500 max-w-md mx-auto mb-8">
            Twoja książka kucharska jest jeszcze pusta. Dodaj swój pierwszy przepis, aby zacząć!
          </p>
          <Link
            to="/add"
            className="inline-flex items-center px-6 py-3 rounded-xl font-medium text-white bg-accent hover:bg-accent/90 transition-colors shadow-sm shadow-accent/30"
          >
            <Plus className="w-5 h-5 mr-2" />
            Dodaj pierwszy przepis
          </Link>
        </div>
      ) : (
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
                  src={recipe.thumbnail_url}
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
              
              {/* Status Badges */}
              {recipe.status === 'failed' && (
                <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1.5 rounded-full flex items-center space-x-1.5 shadow-lg z-10 animate-in fade-in zoom-in duration-300">
                  <AlertTriangle size={14} className="flex-shrink-0" />
                  <span className="text-[10px] font-bold tracking-wider uppercase">BŁĄD</span>
                </div>
              )}
              {(recipe.status === 'processing' || recipe.status === 'pending') && (
                <div className="absolute top-4 right-4 bg-brand-500 text-white px-3 py-1.5 rounded-full flex items-center space-x-1.5 shadow-lg z-10 animate-pulse">
                  <RefreshCw size={14} className="animate-spin flex-shrink-0" />
                  <span className="text-[10px] font-bold tracking-wider uppercase">PRZETWARZANIE</span>
                </div>
              )}
            </div>

            {/* Content */}
            <div className="p-6 flex flex-col flex-grow">
              <h2 className="text-xl font-bold text-gray-900 leading-tight mb-3 group-hover:text-accent transition-colors line-clamp-2">
                {recipe.title || "Przepis bez tytułu"}
              </h2>
              <p className="text-sm text-gray-500 line-clamp-2 mb-4 flex-grow">
                {recipe.short_text || "Brak krótkiego opisu."}
              </p>
              
              {/* Tags on Card */}
              {recipe.tags && recipe.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {recipe.tags.slice(0, 3).map(tag => (
                    <span 
                      key={tag.id} 
                      className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-brand-50 text-brand-600 border border-brand-100"
                    >
                      <TagIcon size={10} className="mr-1" />
                      {tag.name}
                    </span>
                  ))}
                  {recipe.tags.length > 3 && (
                    <span className="text-[10px] text-gray-400 font-medium self-center">
                      +{recipe.tags.length - 3}
                    </span>
                  )}
                </div>
              )}
              
              <div className="mt-auto pt-4 border-t border-gray-100 flex items-center text-sm font-medium text-accent">
                ZOBACZ PRZEPIS <span className="ml-2 transform group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    )}
      
      <TagManagerModal 
        isOpen={showTagManager} 
        onClose={() => setShowTagManager(false)} 
        onTagsChanged={fetchTags}
      />
    </div>
  );
};
