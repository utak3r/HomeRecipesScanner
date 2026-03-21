import React, { useState, useEffect } from 'react';
import { X, Plus, Pencil, Trash2, AlertTriangle, Check, Loader2 } from 'lucide-react';
import api from '../services/api';

interface Tag {
  id: number;
  name: string;
  recipe_count: number;
}

interface TagManagerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTagsChanged: () => void;
}

export const TagManagerModal: React.FC<TagManagerModalProps> = ({ isOpen, onClose, onTagsChanged }) => {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingTagId, setEditingTagId] = useState<number | null>(null);
  const [editTagName, setEditTagName] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [deletingTagId, setDeletingTagId] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchTags = async () => {
    setLoading(true);
    try {
      const res = await api.get('/tags/');
      setTags(res.data);
    } catch (err) {
      console.error('Failed to fetch tags:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchTags();
    }
  }, [isOpen]);


  const handleEditTag = async (tagId: number) => {
    if (!editTagName.trim()) return;

    setIsEditing(true);
    try {
      await api.put(`/tags/${tagId}`, { tags: [editTagName.trim()] });
      setEditingTagId(null);
      fetchTags();
      onTagsChanged();
    } catch (err) {
      console.error('Failed to edit tag:', err);
      alert('Nie udało się zmienić nazwy tagu.');
    } finally {
      setIsEditing(false);
    }
  };

  const handleDeleteTag = async (tagId: number) => {
    setIsDeleting(true);
    try {
      await api.delete(`/tags/${tagId}`);
      setDeletingTagId(null);
      fetchTags();
      onTagsChanged();
    } catch (err) {
      console.error('Failed to delete tag:', err);
      alert('Nie udało się usunąć tagu.');
    } finally {
      setIsDeleting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-[2rem] shadow-2xl w-full max-w-2xl flex flex-col max-h-[90vh] overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-8 py-6 border-b border-gray-100 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-brand-50 text-brand-600 rounded-full flex items-center justify-center font-bold">
              <Pencil className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Zarządzaj Tagami</h2>
              <p className="text-sm text-gray-500">Dodawaj, edytuj i usuwaj tagi ze swojej bazy.</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full text-gray-400 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Tags List */}
        <div className="flex-grow overflow-y-auto px-4 py-4 custom-scrollbar">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
              <Loader2 className="w-10 h-10 text-accent animate-spin" />
              <p className="text-gray-500 font-medium">Wczytywanie tagów...</p>
            </div>
          ) : tags.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-gray-400">Brak tagów w bazie.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-2">
              {tags.map((tag) => (
                <div 
                  key={tag.id}
                  className="flex items-center justify-between p-4 bg-white hover:bg-gray-50 rounded-2xl border border-transparent hover:border-gray-100 transition-all group"
                >
                  <div className="flex-grow flex items-center mr-4">
                    {editingTagId === tag.id ? (
                      <div className="flex items-center gap-2 w-full">
                        <input
                          type="text"
                          value={editTagName}
                          onChange={(e) => setEditTagName(e.target.value)}
                          className="flex-grow px-3 py-1.5 border border-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-accent/20"
                          autoFocus
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleEditTag(tag.id);
                            if (e.key === 'Escape') setEditingTagId(null);
                          }}
                        />
                        <button 
                          onClick={() => handleEditTag(tag.id)}
                          className="p-1.5 text-green-600 hover:bg-green-50 rounded-lg"
                        >
                          <Check className="w-5 h-5" />
                        </button>
                        <button 
                          onClick={() => setEditingTagId(null)}
                          className="p-1.5 text-gray-400 hover:bg-gray-100 rounded-lg"
                        >
                          <X className="w-5 h-5" />
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-3">
                        <span className="font-semibold text-gray-800 text-lg">{tag.name}</span>
                        <span className="text-xs font-medium text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                          {tag.recipe_count} {tag.recipe_count === 1 ? 'przepis' : (tag.recipe_count >= 2 && tag.recipe_count <= 4 ? 'przepisy' : 'przepisów')}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {editingTagId !== tag.id && (
                      <>
                        <button
                          onClick={() => {
                            setEditingTagId(tag.id);
                            setEditTagName(tag.name);
                          }}
                          className="p-2 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-xl transition-colors"
                          title="Edytuj"
                        >
                          <Pencil className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => setDeletingTagId(tag.id)}
                          className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors"
                          title="Usuń"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Overlay */}
      {deletingTagId && (
        <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-[2rem] p-8 max-w-md w-full shadow-2xl relative animate-in zoom-in-95 duration-200">
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="w-16 h-16 bg-red-100 text-red-500 rounded-full flex items-center justify-center mb-2">
                <AlertTriangle className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">Usuń tag</h3>
              <p className="text-gray-500 text-lg leading-relaxed">
                Czy jesteś pewien, że chcesz usunąć tag <span className="font-bold text-gray-900">"{tags.find(t => t.id === deletingTagId)?.name}"</span>?<br/>
                <span className="text-sm mt-2 block">Spowoduje to usunięcie go ze wszystkich przepisów, które go zawierają.</span>
              </p>
              
              <div className="flex w-full gap-4 mt-8 pt-4">
                <button
                  onClick={() => setDeletingTagId(null)}
                  disabled={isDeleting}
                  className="flex-1 px-6 py-3 rounded-xl font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors disabled:opacity-50"
                >
                  Anuluj
                </button>
                <button
                  onClick={() => handleDeleteTag(deletingTagId)}
                  disabled={isDeleting}
                  className="flex-1 px-6 py-3 rounded-xl font-medium text-white bg-red-500 hover:bg-red-600 transition-colors shadow-sm shadow-red-500/30 flex justify-center items-center disabled:opacity-50"
                >
                  {isDeleting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Usuń tag'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
