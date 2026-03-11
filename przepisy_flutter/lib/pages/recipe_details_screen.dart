import 'package:flutter/material.dart';
import '../services/api_service.dart';

class RecipeDetailsScreen extends StatelessWidget {
  final int recipeId;
  const RecipeDetailsScreen({super.key, required this.recipeId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Szczegóły przepisu')),
      body: FutureBuilder<Map<String, dynamic>>(
        future: ApiService().fetchFullRecipe(recipeId),
        builder: (context, snapshot) {
          if (!snapshot.hasData)
            return const Center(child: CircularProgressIndicator());

          var recipe = snapshot.data!;
          var structured = recipe['structured'] ?? {};
          var ingredients = structured['ingredients'] as List? ?? [];
          var steps = structured['steps'] as List? ?? [];

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  recipe['title'] ?? 'Bez tytułu',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 20),
                const Text(
                  'Składniki:',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                ...ingredients.map(
                  (ing) => Text('• ${ing['amount']} ${ing['name']}'),
                ),
                const SizedBox(height: 20),
                const Text(
                  'Przygotowanie:',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                ...steps.asMap().entries.map(
                  (entry) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Text('${entry.key + 1}. ${entry.value}'),
                  ),
                ),
                // Twoje zdjęcia na końcu
                if (recipe['images'] != null) ...[
                  const SizedBox(height: 20),
                  const Text(
                    'Skany:',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  ...recipe['images'].map(
                    (img) =>
                        Image.network('${ApiService.baseUrl}${img['url']}'),
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }
}
