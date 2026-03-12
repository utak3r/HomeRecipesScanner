import 'package:flutter/material.dart';
import 'dart:async';
import '../services/api_service.dart';
import 'edit_recipe_content_screen.dart';

class RecipeDetailsScreen extends StatefulWidget {
  final int recipeId;
  const RecipeDetailsScreen({super.key, required this.recipeId});

  @override
  State<RecipeDetailsScreen> createState() => _RecipeDetailsScreenState();
}

class _RecipeDetailsScreenState extends State<RecipeDetailsScreen> {
  Future<Map<String, dynamic>>? _recipeFuture;
  Timer? _statusTimer;
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    _fetchRecipe();
  }

  @override
  void dispose() {
    _statusTimer?.cancel();
    super.dispose();
  }

  void _fetchRecipe() {
    setState(() {
      _recipeFuture = ApiService().fetchFullRecipe(widget.recipeId);
    });
    
    _recipeFuture?.then((recipe) {
      if (recipe['status'] == 'processed' && _isProcessing) {
        setState(() {
          _isProcessing = false;
        });
        _statusTimer?.cancel();
      } else if (recipe['status'] != 'processed') {
         if (!_isProcessing) {
             setState(() {
                _isProcessing = true;
             });
         }
         _startPolling();
      }
    });
  }
  
  void _startPolling() {
      if (_statusTimer == null || !_statusTimer!.isActive) {
          _statusTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
             _fetchRecipe();
          });
      }
  }

  void _refreshRecipe() {
    _fetchRecipe();
  }

  void _showEditTitleDialog(String currentTitle) {
    final TextEditingController titleController =
        TextEditingController(text: currentTitle);

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Edytuj tytuł'),
          content: TextField(
            controller: titleController,
            decoration: const InputDecoration(labelText: 'Tytuł przepisu'),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Anuluj'),
            ),
            ElevatedButton(
              onPressed: () async {
                try {
                  await ApiService().updateRecipeTitle(
                    widget.recipeId,
                    titleController.text,
                  );
                  if (context.mounted) {
                    Navigator.pop(context);
                    _refreshRecipe();
                  }
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Błąd: $e')),
                    );
                  }
                }
              },
              child: const Text('Zapisz'),
            ),
          ],
        );
      },
    );
  }

  void _confirmReprocess() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Odczytaj jeszcze raz'),
          content: const Text(
            'Uwaga! Wybranie tej opcji spowoduje nadpisanie wszystkich danych tekstowych!',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Anuluj'),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(context); // Zamknij dialog
                try {
                  await ApiService().reprocessRecipe(widget.recipeId);
                  setState(() {
                     _isProcessing = true;
                  });
                  _startPolling();
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Błąd: $e')),
                    );
                  }
                }
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              child: const Text('Zatwierdź', style: TextStyle(color: Colors.white)),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>>(
      future: _recipeFuture,
      builder: (context, snapshot) {
        if (!snapshot.hasData) {
          return Scaffold(
            appBar: AppBar(title: const Text('Szczegóły przepisu')),
            body: const Center(child: CircularProgressIndicator()),
          );
        }

        var recipe = snapshot.data!;
        var structured = recipe['structured'] ?? {};
        var ingredients = structured['ingredients'] as List? ?? [];
        var steps = structured['steps'] as List? ?? [];
        String currentTitle = recipe['title'] ?? 'Bez tytułu';

        return Scaffold(
          appBar: AppBar(
            title: const Text('Szczegóły przepisu'),
            actions: [
              PopupMenuButton<String>(
                onSelected: (value) async {
                  if (value == 'edit_title') {
                    _showEditTitleDialog(currentTitle);
                  } else if (value == 'edit_content') {
                    final result = await Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => EditRecipeContentScreen(
                          recipeId: widget.recipeId,
                          initialStructured:
                              Map<String, dynamic>.from(structured),
                        ),
                      ),
                    );
                    if (result == true) {
                      _refreshRecipe();
                    }
                  } else if (value == 'reprocess') {
                    _confirmReprocess();
                  }
                },
                itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: 'edit_title',
                    child: Text('Edytuj tytuł'),
                  ),
                  const PopupMenuItem(
                    value: 'edit_content',
                    child: Text('Edytuj treść przepisu'),
                  ),
                  const PopupMenuItem(
                    value: 'reprocess',
                    child: Text('Odczytaj jeszcze raz'),
                  ),
                ],
              ),
            ],
          ),
          body: _isProcessing
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(),
                      SizedBox(height: 16),
                      Text('Trwa odczytywanie tekstu ze zdjęć...'),
                    ],
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        currentTitle,
                        style: Theme.of(context).textTheme.headlineMedium,
                      ),
                      const SizedBox(height: 20),
                      const Text(
                        'Składniki:',
                        style: TextStyle(
                            fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      ...ingredients.map(
                        (ing) => Text('• ${ing['amount']} ${ing['name']}'),
                      ),
                      const SizedBox(height: 20),
                      const Text(
                        'Przygotowanie:',
                        style: TextStyle(
                            fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      ...steps.asMap().entries.map(
                            (entry) => Padding(
                              padding: const EdgeInsets.symmetric(vertical: 4),
                              child: Text('${entry.key + 1}. ${entry.value}'),
                            ),
                          ),
                      if (structured['notes'] != null &&
                          structured['notes'].toString().isNotEmpty) ...[
                        const SizedBox(height: 20),
                        const Text(
                          'Notatki:',
                          style: TextStyle(
                              fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          structured['notes'],
                          style: const TextStyle(fontStyle: FontStyle.italic),
                        ),
                      ],
                      // Twoje zdjęcia na końcu
                      if (recipe['images'] != null) ...[
                        const SizedBox(height: 20),
                        const Text(
                          'Skany:',
                          style: TextStyle(
                              fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        ...recipe['images'].map(
                          (img) => Image.network(
                              '${ApiService.baseUrl}${img['url']}'),
                        ),
                      ],
                    ],
                  ),
                ),
        );
      },
    );
  }
}
