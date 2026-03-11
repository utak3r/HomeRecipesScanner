export interface Ingredient {
  name: string;
  amount: string;
}

export interface StructuredRecipe {
  title?: string;
  notes?: string;
  steps?: string[];
  ingredients?: Ingredient[];
}

export interface RecipeImage {
  id: number;
  url: string;
}

export interface Recipe {
  id: number;
  title: string;
  thumbnail_url: string;
  short_text: string;
  status: string;
  structured?: StructuredRecipe;
  images?: RecipeImage[];
}
