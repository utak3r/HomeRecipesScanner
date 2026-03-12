import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { RecipeList } from './pages/RecipeList';
import { RecipeDetail } from './pages/RecipeDetail';
import { AddRecipe } from './pages/AddRecipe';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-orange-600 text-white p-4 shadow-md">
          <div className="container mx-auto">
            <Link to="/" className="text-2xl font-bold flex items-center gap-3 group">
              <div className="bg-white p-0.5 rounded-xl shadow-sm group-hover:shadow-md transition-shadow">
                <img src="/ikonka_1024px.png" alt="Logo" className="w-12 h-12 rounded-[0.6rem]" />
              </div>
              <span className="drop-shadow-sm tracking-tight text-white/95 group-hover:text-white transition-colors">Książka Kucharska</span>
            </Link>
          </div>
        </nav>

        <main className="container mx-auto py-6">
          <Routes>
            <Route path="/" element={<RecipeList />} />
            <Route path="/add" element={<AddRecipe />} />
            <Route path="/recipe/:id" element={<RecipeDetail />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
