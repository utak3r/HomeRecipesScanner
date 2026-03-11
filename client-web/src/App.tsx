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
            <Link to="/" className="text-2xl font-bold">Książka Kucharska</Link>
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
