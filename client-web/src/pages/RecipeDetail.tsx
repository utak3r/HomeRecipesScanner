import { useEffect, useState, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Recipe } from '../types/recipe';
import { ArrowLeft, ChefHat, Info, Maximize2, MoreVertical, Trash2, AlertTriangle, X, Pencil, RefreshCw, Edit3, PlusCircle, ChevronUp, ChevronDown } from 'lucide-react';

export const RecipeDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState<Recipe | null>(null);

  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showEditTitleModal, setShowEditTitleModal] = useState(false);
  const [editTitleValue, setEditTitleValue] = useState("");
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [showReprocessConfirm, setShowReprocessConfirm] = useState(false);
  const [isReprocessing, setIsReprocessing] = useState(false);
  const [showEditStructuredModal, setShowEditStructuredModal] = useState(false);
  const [editStructured, setEditStructured] = useState<Recipe['structured'] | null>(null);
  const [isSavingStructured, setIsSavingStructured] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.get(`/recipes/${id}`).then(res => setRecipe(res.data));
  }, [id]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleDelete = async () => {
    try {
      setIsDeleting(true);
      await api.delete(`/recipes/${id}`);
      navigate('/');
    } catch (error) {
      console.error('Failed to delete recipe:', error);
      alert('Nie udało się usunąć przepisu.');
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  const handleEditTitle = async () => {
    try {
      setIsEditingTitle(true);
      await api.put(`/recipes/${id}`, { title: editTitleValue });
      
      const res = await api.get(`/recipes/${id}`);
      setRecipe(res.data);
      
      setShowEditTitleModal(false);
    } catch (error) {
      console.error('Failed to update title:', error);
      alert('Nie udało się zaktualizować tytułu.');
    } finally {
      setIsEditingTitle(false);
    }
  };

  const handleReprocess = async () => {
    try {
      setIsReprocessing(true);
      await api.post(`/recipes/${id}/reprocess`);
      setRecipe(prev => prev ? { ...prev, status: 'processing' } : prev);
    } catch (error) {
      console.error('Failed to start reprocessing:', error);
      alert('Nie udało się rozpocząć ponownego przetwarzania.');
      setIsReprocessing(false);
      setShowReprocessConfirm(false);
    }
  };

  const handleSaveStructured = async () => {
    if (!editStructured) return;

    try {
      setIsSavingStructured(true);
      
      // Filtrowanie pustych składników i kroków
      const cleanedStructured = {
        ...editStructured,
        ingredients: editStructured.ingredients?.filter(ing => ing.name?.trim() !== ''),
        steps: editStructured.steps?.filter(step => step?.trim() !== '')
      };

      await api.put(`/recipes/${id}`, { structured: cleanedStructured });
      
      const res = await api.get(`/recipes/${id}`);
      setRecipe(res.data);
      
      setShowEditStructuredModal(false);
    } catch (error) {
      console.error('Failed to update structured content:', error);
      alert('Nie udało się zapisać treści przepisu.');
    } finally {
      setIsSavingStructured(false);
    }
  };

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;
    
    if (recipe?.status === 'processing' || recipe?.status === 'pending') {
      intervalId = setInterval(async () => {
        try {
          const res = await api.get(`/recipes/${id}`);
          setRecipe(res.data);
          if (res.data.status !== 'processing' && res.data.status !== 'pending') {
            setIsReprocessing(false);
            setShowReprocessConfirm(false);
            clearInterval(intervalId);
          }
        } catch (error) {
          console.error('Failed to poll status', error);
        }
      }, 3000);
    }

    return () => clearInterval(intervalId);
  }, [recipe?.status, id]);

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
          <div className="flex justify-between items-start mb-12">
            <Link 
              to="/" 
              className="inline-flex items-center text-sm text-gray-400 hover:text-accent font-semibold tracking-wide uppercase transition-colors group"
            >
              <ArrowLeft className="w-4 h-4 mr-2 transform group-hover:-translate-x-1 transition-transform" />
              Wróć do przepisów
            </Link>

            {/* Dropdown Menu */}
            <div className="relative" ref={menuRef}>
              <button 
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-white/50 text-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-accent/20"
                aria-label="Opcje przepisu"
              >
                <MoreVertical className="w-6 h-6" />
              </button>

              {isMenuOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                  <button
                    onClick={() => {
                      setIsMenuOpen(false);
                      setEditTitleValue(recipe.title || recipe.structured?.title || "");
                      setShowEditTitleModal(true);
                    }}
                    className="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 flex items-center transition-colors font-medium border-b border-gray-100"
                  >
                    <Pencil className="w-4 h-4 mr-2 flex-shrink-0" />
                    Edytuj tytuł
                  </button>
                  <button
                    onClick={() => {
                      setIsMenuOpen(false);
                      // Inicjalizacja kopii do edycji, unikając nulla
                      setEditStructured(recipe.structured ? JSON.parse(JSON.stringify(recipe.structured)) : { ingredients: [], steps: [], notes: '' });
                      setShowEditStructuredModal(true);
                    }}
                    className="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 flex items-center transition-colors font-medium border-b border-gray-100"
                  >
                    <Edit3 className="w-4 h-4 mr-2 flex-shrink-0" />
                    Edytuj treść przepisu
                  </button>
                  <button
                    onClick={() => {
                      setIsMenuOpen(false);
                      setShowReprocessConfirm(true);
                    }}
                    className="w-full text-left px-4 py-2.5 text-sm text-brand-600 hover:bg-brand-50 flex items-center transition-colors font-medium border-b border-gray-100"
                  >
                    <RefreshCw className="w-4 h-4 mr-2 flex-shrink-0" />
                    Przeskanuj i przeczytaj jeszcze raz
                  </button>
                  <button
                    onClick={() => {
                      setIsMenuOpen(false);
                      setShowDeleteConfirm(true);
                    }}
                    className="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 flex items-center transition-colors font-medium"
                  >
                    <Trash2 className="w-4 h-4 mr-2 flex-shrink-0" />
                    Usuń przepis
                  </button>
                </div>
              )}
            </div>
          </div>

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
        {(recipe.status === 'processing' || recipe.status === 'pending') && (
          <div className="mb-8 p-6 bg-brand-50 border border-brand-200 rounded-[2rem] flex items-center space-x-4 text-brand-800 shadow-sm animate-pulse">
            <RefreshCw className="w-6 h-6 animate-spin flex-shrink-0 text-brand-600" />
            <span className="font-medium text-lg">Receptura jest rozpoznawana. To może zająć kilkadziesiąt sekund...</span>
          </div>
        )}

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

      {/* Edit Title Modal */}
      {showEditTitleModal && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-[2rem] p-8 max-w-md w-full shadow-2xl relative animate-in zoom-in-95 duration-200">
            <button 
              onClick={() => setShowEditTitleModal(false)}
              className="absolute top-6 right-6 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            
            <div className="flex flex-col space-y-4 mt-2">
              <div className="flex items-center space-x-3 mb-2">
                <div className="w-10 h-10 bg-brand-50 text-brand-600 rounded-full flex items-center justify-center">
                  <Pencil className="w-5 h-5" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">Edytuj tytuł</h3>
              </div>
              
              <div className="space-y-2 mt-4">
                <label className="text-sm font-medium text-gray-700">Tytuł przepisu</label>
                <input
                  type="text"
                  value={editTitleValue}
                  onChange={(e) => setEditTitleValue(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent transition-all text-gray-800"
                  placeholder="Wpisz nowy tytuł..."
                  autoFocus
                />
              </div>
              
              <div className="flex w-full gap-4 mt-8 pt-4">
                <button
                  onClick={() => setShowEditTitleModal(false)}
                  disabled={isEditingTitle}
                  className="flex-1 px-6 py-3 rounded-xl font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors disabled:opacity-50"
                >
                  Anuluj
                </button>
                <button
                  onClick={handleEditTitle}
                  disabled={isEditingTitle || !editTitleValue.trim()}
                  className="flex-1 px-6 py-3 rounded-xl font-medium text-white bg-accent hover:bg-accent/90 transition-colors shadow-sm shadow-accent/30 flex justify-center items-center disabled:opacity-50"
                >
                  {isEditingTitle ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  ) : (
                    'Zmień tytuł'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Reprocess Confirmation Modal */}
      {showReprocessConfirm && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-[2rem] p-8 max-w-md w-full shadow-2xl relative animate-in zoom-in-95 duration-200">
            <button 
              onClick={() => !isReprocessing && setShowReprocessConfirm(false)}
              className="absolute top-6 right-6 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
              disabled={isReprocessing}
            >
              <X className="w-5 h-5" />
            </button>
            
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="w-16 h-16 bg-brand-100 text-brand-600 rounded-full flex items-center justify-center mb-2">
                <RefreshCw className={`w-8 h-8 ${isReprocessing ? 'animate-spin' : ''}`} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">Ponowne skanowanie</h3>
              <p className="text-gray-500 text-lg leading-relaxed">
                Uwaga, wybranie tej opcji spowoduje <span className="font-semibold text-brand-600">nadpisanie wszystkich danych tekstowych!</span>
              </p>
              
              <div className="flex w-full gap-4 mt-8 pt-4">
                <button
                  onClick={() => setShowReprocessConfirm(false)}
                  disabled={isReprocessing}
                  className="flex-1 px-6 py-3 rounded-xl font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors disabled:opacity-50"
                >
                  Anuluj
                </button>
                <button
                  onClick={handleReprocess}
                  disabled={isReprocessing}
                  className="flex-1 px-6 py-3 rounded-xl font-medium text-white bg-brand-600 hover:bg-brand-700 transition-colors shadow-sm shadow-brand-600/30 flex justify-center items-center disabled:opacity-50"
                >
                  {isReprocessing ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  ) : (
                    'Zatwierdź'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-[2rem] p-8 max-w-md w-full shadow-2xl relative animate-in zoom-in-95 duration-200">
            <button 
              onClick={() => setShowDeleteConfirm(false)}
              className="absolute top-6 right-6 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="w-16 h-16 bg-red-100 text-red-500 rounded-full flex items-center justify-center mb-2">
                <AlertTriangle className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">Usuń przepis</h3>
              <p className="text-gray-500 text-lg leading-relaxed">
                Czy jesteś pewien, że chcesz usunąć przepis? <br/>
                <span className="font-semibold text-red-500">Wszystkie dane zostaną utracone!</span>
              </p>
              
              <div className="flex w-full gap-4 mt-8 pt-4">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={isDeleting}
                  className="flex-1 px-6 py-3 rounded-xl font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors disabled:opacity-50"
                >
                  Anuluj
                </button>
                <button
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="flex-1 px-6 py-3 rounded-xl font-medium text-white bg-red-500 hover:bg-red-600 transition-colors shadow-sm shadow-red-500/30 flex justify-center items-center disabled:opacity-50"
                >
                  {isDeleting ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  ) : (
                    'Usuń'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Structured Content Modal */}
      {showEditStructuredModal && editStructured && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-[2rem] p-8 rounded-t-[2rem] max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl relative animate-in zoom-in-95 duration-200 overflow-hidden">
            
            {/* Modal Header */}
            <div className="flex justify-between items-center mb-6 pb-4 border-b border-gray-100 shrink-0">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-brand-50 text-brand-600 rounded-full flex items-center justify-center">
                  <Edit3 className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">Edytuj treść przepisu</h3>
                  <p className="text-gray-500 text-sm">Popraw odczytane składniki i kroki wykonania.</p>
                </div>
              </div>
              <button 
                onClick={() => !isSavingStructured && setShowEditStructuredModal(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
                disabled={isSavingStructured}
              >
                <X className="w-8 h-8" />
              </button>
            </div>
            
            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto pr-4 space-y-10 min-h-0 custom-scrollbar">
              
              {/* Ingredients Section */}
              <section>
                <h4 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <div className="w-2 h-6 bg-accent rounded-full mr-3"></div>
                  Składniki
                </h4>
                <div className="space-y-3">
                  {editStructured.ingredients?.map((ing, idx) => (
                    <div key={idx} className="flex items-start gap-3 group">
                      <input
                        type="text"
                        value={ing.name || ''}
                        onChange={(e) => {
                          const newIngs = [...(editStructured.ingredients || [])];
                          newIngs[idx] = { ...newIngs[idx], name: e.target.value };
                          setEditStructured({ ...editStructured, ingredients: newIngs });
                        }}
                        className="flex-grow px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent transition-all text-gray-800"
                        placeholder="Nazwa składnika"
                      />
                      <input
                        type="text"
                        value={ing.amount || ''}
                        onChange={(e) => {
                          const newIngs = [...(editStructured.ingredients || [])];
                          newIngs[idx] = { ...newIngs[idx], amount: e.target.value };
                          setEditStructured({ ...editStructured, ingredients: newIngs });
                        }}
                        className="w-1/3 px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent transition-all text-gray-800"
                        placeholder="Ilość"
                      />
                      <div className="flex flex-col gap-1 shrink-0">
                        <button
                          onClick={() => {
                            if (idx === 0) return;
                            const newIngs = [...(editStructured.ingredients || [])];
                            [newIngs[idx - 1], newIngs[idx]] = [newIngs[idx], newIngs[idx - 1]];
                            setEditStructured({ ...editStructured, ingredients: newIngs });
                          }}
                          disabled={idx === 0}
                          className="p-1 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-gray-400"
                          title="Przesuń wyżej"
                        >
                          <ChevronUp className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => {
                            if (idx === (editStructured.ingredients?.length || 0) - 1) return;
                            const newIngs = [...(editStructured.ingredients || [])];
                            [newIngs[idx + 1], newIngs[idx]] = [newIngs[idx], newIngs[idx + 1]];
                            setEditStructured({ ...editStructured, ingredients: newIngs });
                          }}
                          disabled={idx === (editStructured.ingredients?.length || 0) - 1}
                          className="p-1 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-gray-400"
                          title="Przesuń niżej"
                        >
                          <ChevronDown className="w-5 h-5" />
                        </button>
                      </div>
                      <button
                        onClick={() => {
                          const newIngs = editStructured.ingredients?.filter((_, i) => i !== idx);
                          setEditStructured({ ...editStructured, ingredients: newIngs });
                        }}
                        className="p-3 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors shrink-0 self-center"
                        title="Usuń składnik"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => {
                      const newIngs = [...(editStructured.ingredients || []), { name: '', amount: '' }];
                      setEditStructured({ ...editStructured, ingredients: newIngs });
                    }}
                    className="inline-flex items-center text-accent font-medium hover:text-accent/80 transition-colors mt-2"
                  >
                    <PlusCircle className="w-5 h-5 mr-2" />
                    Dodaj składnik
                  </button>
                </div>
              </section>

              {/* Steps Section */}
              <section>
                <h4 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <div className="w-2 h-6 bg-brand-400 rounded-full mr-3"></div>
                  Kroki przygotowania
                </h4>
                <div className="space-y-4">
                  {editStructured.steps?.map((step, idx) => (
                    <div key={idx} className="flex gap-4 items-start group">
                      <div className="shrink-0 w-8 h-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center font-bold text-sm mt-2">
                        {idx + 1}
                      </div>
                      <textarea
                        value={step || ''}
                        onChange={(e) => {
                          const newSteps = [...(editStructured.steps || [])];
                          newSteps[idx] = e.target.value;
                          setEditStructured({ ...editStructured, steps: newSteps });
                          
                          // Proste auto-resize dla textarea
                          e.target.style.height = 'auto';
                          e.target.style.height = e.target.scrollHeight + 'px';
                        }}
                        className="flex-grow px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-brand-400/50 focus:border-brand-400 transition-all text-gray-800 min-h-[80px] resize-none overflow-hidden"
                        placeholder="Opisz ten krok..."
                        onKeyDown={(e) => {
                           if(e.currentTarget) {
                             e.currentTarget.style.height = 'auto';
                             e.currentTarget.style.height = e.currentTarget.scrollHeight + 'px';
                           }
                        }}
                      />
                      <div className="flex flex-col gap-1 shrink-0 mt-1">
                        <button
                          onClick={() => {
                            if (idx === 0) return;
                            const newSteps = [...(editStructured.steps || [])];
                            [newSteps[idx - 1], newSteps[idx]] = [newSteps[idx], newSteps[idx - 1]];
                            setEditStructured({ ...editStructured, steps: newSteps });
                          }}
                          disabled={idx === 0}
                          className="p-1 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-gray-400"
                          title="Przesuń wyżej"
                        >
                          <ChevronUp className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => {
                            if (idx === (editStructured.steps?.length || 0) - 1) return;
                            const newSteps = [...(editStructured.steps || [])];
                            [newSteps[idx + 1], newSteps[idx]] = [newSteps[idx], newSteps[idx + 1]];
                            setEditStructured({ ...editStructured, steps: newSteps });
                          }}
                          disabled={idx === (editStructured.steps?.length || 0) - 1}
                          className="p-1 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-gray-400"
                          title="Przesuń niżej"
                        >
                          <ChevronDown className="w-5 h-5" />
                        </button>
                      </div>
                      <button
                        onClick={() => {
                          const newSteps = editStructured.steps?.filter((_, i) => i !== idx);
                          setEditStructured({ ...editStructured, steps: newSteps });
                        }}
                        className="p-3 mt-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors shrink-0 self-center"
                        title="Usuń krok"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => {
                      const newSteps = [...(editStructured.steps || []), ''];
                      setEditStructured({ ...editStructured, steps: newSteps });
                    }}
                    className="inline-flex items-center text-brand-600 font-medium hover:text-brand-500 transition-colors mt-2"
                  >
                    <PlusCircle className="w-5 h-5 mr-2" />
                    Dodaj krok
                  </button>
                </div>
              </section>

              {/* Notes Section */}
              <section>
                <h4 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <div className="w-2 h-6 bg-yellow-400 rounded-full mr-3"></div>
                  Wskazówki autora
                </h4>
                <textarea
                  value={editStructured.notes || ''}
                  onChange={(e) => {
                    setEditStructured({ ...editStructured, notes: e.target.value });
                    e.target.style.height = 'auto';
                    e.target.style.height = e.target.scrollHeight + 'px';
                  }}
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 focus:border-yellow-400 transition-all text-gray-800 min-h-[100px] resize-none overflow-hidden"
                  placeholder="Dodatkowe informacje, sekrety kucharza..."
                />
              </section>

            </div>

            {/* Modal Footer / Actions */}
            <div className="mt-8 pt-6 border-t border-gray-100 flex gap-4 shrink-0">
              <button
                onClick={() => setShowEditStructuredModal(false)}
                disabled={isSavingStructured}
                className="flex-1 px-6 py-4 rounded-xl font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors disabled:opacity-50"
              >
                Zrezygnuj
              </button>
              <button
                onClick={handleSaveStructured}
                disabled={isSavingStructured}
                className="flex-[2] px-6 py-4 rounded-xl font-bold text-white bg-accent hover:bg-accent/90 transition-all shadow-md shadow-accent/30 flex justify-center items-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none"
              >
                {isSavingStructured ? (
                  <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                ) : (
                  'Zapisz zmiany przepisu'
                )}
              </button>
            </div>
            
          </div>
        </div>
      )}
    </div>
  );
};
