import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, ImagePlus, X, Send, AlertTriangle, Maximize2 } from 'lucide-react';
import { 
  DndContext, 
  closestCenter, 
  KeyboardSensor, 
  PointerSensor, 
  useSensor, 
  useSensors,
  DragEndEvent
} from '@dnd-kit/core';
import { 
  arrayMove, 
  SortableContext, 
  sortableKeyboardCoordinates, 
  verticalListSortingStrategy,
  horizontalListSortingStrategy
} from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import api from '../services/api';

// --- Sortable Item Component ---
interface SortableImageProps {
  id: string;
  file: File;
  previewUrl: string;
  onRemove: (id: string) => void;
  onZoom: (url: string) => void;
}

const SortableImage = ({ id, file, previewUrl, onRemove, onZoom }: SortableImageProps) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 10 : 1,
    opacity: isDragging ? 0.8 : 1,
  };

  return (
    <div 
      ref={setNodeRef} 
      style={style} 
      className={`relative group rounded-2xl overflow-hidden border-2 ${isDragging ? 'border-accent scale-105 shadow-xl' : 'border-gray-200'} bg-white aspect-[3/4] max-w-[500px] mx-auto w-full flex-shrink-0 cursor-grab active:cursor-grabbing`}
      {...attributes}
      {...listeners}
    >
      <img src={previewUrl} alt="Podgląd" className="w-full h-full object-cover" />
      
      {/* Overlay Actions - Need to stop propagation so drag doesn't catch these clicks */}
      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center p-4">
        <div className="flex space-x-4">
          <button 
            type="button"
            onClick={(e) => { e.stopPropagation(); onZoom(previewUrl); }}
            className="w-12 h-12 flex items-center justify-center bg-white/20 hover:bg-white/40 backdrop-blur-md rounded-full text-white transition-all transform hover:scale-110"
            aria-label="Powiększ"
          >
            <Maximize2 className="w-6 h-6" />
          </button>
          <button 
            type="button"
            onClick={(e) => { e.stopPropagation(); onRemove(id); }}
            className="w-12 h-12 flex items-center justify-center bg-red-500/80 hover:bg-red-500 backdrop-blur-md rounded-full text-white transition-all transform hover:scale-110 shadow-lg"
            aria-label="Usuń zdjęcie"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
      </div>
      
      {/* Drag Handle Indicator */}
      <div className="absolute top-4 left-4 bg-white/80 backdrop-blur-sm px-3 py-1.5 rounded-lg text-xs font-bold text-gray-700 shadow-sm pointer-events-none">
        Przeciągnij by przenieść
      </div>
    </div>
  );
};


export const AddRecipe = () => {
  const navigate = useNavigate();
  const [images, setImages] = useState<{ id: string; file: File; previewUrl: string }[]>([]);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [showSubmitConfirm, setShowSubmitConfirm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files).map(file => ({
        id: crypto.randomUUID(),
        file,
        previewUrl: URL.createObjectURL(file)
      }));
      setImages(prev => [...prev, ...newFiles]);
    }
    // Resetuj input aby można było dodać ten sam plik klikając ponownie
    e.target.value = '';
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      setImages((items) => {
        const oldIndex = items.findIndex((i) => i.id === active.id);
        const newIndex = items.findIndex((i) => i.id === over.id);
        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  const removeImage = (id: string) => {
    setImages(prev => {
      const imageToRemove = prev.find(img => img.id === id);
      if (imageToRemove) URL.revokeObjectURL(imageToRemove.previewUrl);
      return prev.filter(img => img.id !== id);
    });
  };

  const handleSubmit = async () => {
    try {
      setIsSubmitting(true);
      const formData = new FormData();
      images.forEach((img) => formData.append('files', img.file));

      const res = await api.post<{recipe_id: number, files_count: number, status: string}>('/recipes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      navigate(`/recipe/${res.data.recipe_id}`);
    } catch (error) {
      console.error('Failed to upload recipe:', error);
      alert('Nie udało się wysłać przepisu.');
      setIsSubmitting(false);
      setShowSubmitConfirm(false);
    }
  };

  // Keyboard support for zooming out Modal
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSelectedImage(null);
    };
    if (selectedImage) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'auto';
    };
  }, [selectedImage]);

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-24">
      {/* Header */}
      <div className="relative w-full bg-white border-b border-gray-100 pt-12 pb-12">
        <div className="absolute inset-0 bg-gradient-to-b from-brand-50/50 to-transparent"></div>
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 flex justify-between items-center">
          <div>
            <Link 
              to="/" 
              className="inline-flex items-center text-sm text-gray-400 hover:text-accent font-semibold tracking-wide uppercase transition-colors group mb-6"
            >
              <ArrowLeft className="w-4 h-4 mr-2 transform group-hover:-translate-x-1 transition-transform" />
              Wróć do przepisów
            </Link>
            <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 tracking-tight leading-[1.1]">
              Dodaj nowy przepis
            </h1>
          </div>
          <button
            onClick={() => setShowSubmitConfirm(true)}
            disabled={images.length === 0}
            className="inline-flex items-center px-8 py-4 rounded-xl font-bold text-white bg-accent hover:bg-accent/90 transition-all shadow-lg hover:shadow-accent/40 hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none"
          >
            <Send className="w-5 h-5 mr-3" />
            Wyślij
          </button>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 relative z-20">
        
        {/* Upload Button */}
        <div className="flex justify-center mb-12">
          <label className="cursor-pointer group flex flex-col items-center justify-center w-full max-w-xl h-64 rounded-3xl border-3 border-dashed border-gray-300 hover:border-accent bg-white hover:bg-brand-50/50 transition-all duration-300">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <div className="w-20 h-20 mb-4 rounded-full bg-brand-100 text-accent flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <ImagePlus className="w-10 h-10" />
              </div>
              <p className="mb-2 text-xl font-bold text-gray-700">Skany przepisu</p>
              <p className="text-gray-500 font-medium">Kliknij tutaj aby dodać zdjęcia z dysku</p>
            </div>
            <input 
              type="file" 
              className="hidden" 
              multiple 
              accept="image/*" 
              onChange={handleFileChange} 
            />
          </label>
        </div>

        {/* Drag and Drop Area */}
        {images.length > 0 && (
          <div className="bg-white rounded-[2.5rem] p-8 shadow-sm border border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center">Dodane strony</h2>
            <p className="text-gray-500 text-center mb-10 pb-8 border-b border-gray-100">
              Kolejność jest bardzo ważna! Złap miniaturkę aby ją przeciągnąć i ułożyć w odpowiedniej kolejności czytania przepisu.
            </p>
            
            <DndContext 
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={handleDragEnd}
            >
              <SortableContext 
                items={images.map(img => img.id)}
                strategy={horizontalListSortingStrategy}
              >
                <div className="flex flex-wrap justify-center gap-6">
                  {images.map(img => (
                    <div key={img.id} className="w-[300px] sm:w-[400px] lg:w-[480px]">
                      <SortableImage 
                        id={img.id} 
                        file={img.file} 
                        previewUrl={img.previewUrl} 
                        onRemove={removeImage}
                        onZoom={setSelectedImage} 
                      />
                    </div>
                  ))}
                </div>
              </SortableContext>
            </DndContext>
          </div>
        )}
      </div>

      {/* Submit Confirmation Modal */}
      {showSubmitConfirm && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-[2rem] p-8 max-w-md w-full shadow-2xl relative animate-in zoom-in-95 duration-200">
            <button 
              onClick={() => !isSubmitting && setShowSubmitConfirm(false)}
              className="absolute top-6 right-6 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
              disabled={isSubmitting}
            >
              <X className="w-5 h-5" />
            </button>
            
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="w-16 h-16 bg-brand-100 text-accent rounded-full flex items-center justify-center mb-2">
                <AlertTriangle className={`w-8 h-8 ${isSubmitting ? 'animate-bounce' : ''}`} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">Rozpoznaj przepis</h3>
              <p className="text-gray-500 text-lg leading-relaxed">
                Jesteś pewien, że chcesz wysłać do skanowania i rozpoznania <span className="font-bold text-accent">{images.length} {images.length === 1 ? 'zdjęcie' : (images.length > 1 && images.length < 5) ? 'zdjęcia' : 'zdjęć'}</span>?
              </p>
              
              <div className="flex w-full gap-4 mt-8 pt-4">
                <button
                  onClick={() => setShowSubmitConfirm(false)}
                  disabled={isSubmitting}
                  className="flex-1 px-6 py-3 rounded-xl font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors disabled:opacity-50"
                >
                  Anuluj
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="flex-1 px-6 py-3 rounded-xl font-medium text-white bg-accent hover:bg-accent/90 transition-colors shadow-sm shadow-accent/30 flex justify-center items-center disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  ) : (
                    'Wysyłam'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Image Lightbox Overlay */}
      {selectedImage && (
        <div 
          className="fixed inset-0 z-[70] flex items-center justify-center bg-black/95 p-4 md:p-8 backdrop-blur-md transition-opacity"
          onClick={() => setSelectedImage(null)}
        >
          <button 
            className="absolute top-6 right-6 md:top-10 md:right-10 w-12 h-12 flex items-center justify-center bg-white/10 hover:bg-white/20 text-white rounded-full transition-colors backdrop-blur-md z-[80]"
            onClick={(e) => {
              e.stopPropagation();
              setSelectedImage(null);
            }}
            aria-label="Zamknij"
          >
            <X className="w-6 h-6" />
          </button>
          
          <img 
            src={selectedImage} 
            alt="Powiększony skan przepisu" 
            className="w-auto h-auto max-w-full max-h-[90vh] object-contain rounded-lg shadow-2xl cursor-zoom-out"
            onClick={(e) => {
              e.stopPropagation();
              setSelectedImage(null);
            }}
          />
        </div>
      )}
    </div>
  );
};
