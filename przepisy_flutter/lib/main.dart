import 'package:flutter/material.dart';
import 'dart:async';
import 'services/api_service.dart';
import 'models/recipe.dart';
import 'pages/recipe_details_screen.dart';
import 'pages/upload_recipe_screen.dart';

void main() => runApp(const RecipeApp());

class RecipeApp extends StatelessWidget {
  const RecipeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Domowe Przepisy',
      theme: ThemeData(primarySwatch: Colors.orange),
      home: const RecipeListScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class RecipeListScreen extends StatefulWidget {
  const RecipeListScreen({super.key});

  @override
  _RecipeListScreenState createState() => _RecipeListScreenState();
}

class _RecipeListScreenState extends State<RecipeListScreen> {
  final ApiService apiService = ApiService();
  Timer? _statusTimer;
  List<Recipe> _recipes = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  @override
  void dispose() {
    _statusTimer?.cancel();
    super.dispose();
  }

  Future<void> _fetchData() async {
    try {
      final data = await apiService.fetchRecipes();
      if (!mounted) return;
      setState(() {
        _recipes = data;
        _isLoading = false;
        _error = null;
      });
      _manageTimer();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = 'Błąd: $e';
        _isLoading = false;
      });
      print("Błąd pobierania: $e");
    }
  }

  void _manageTimer() {
    bool hasProcessing = _recipes.any((r) => r.status != 'processed');

    if (hasProcessing && (_statusTimer == null || !_statusTimer!.isActive)) {
      _statusTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
        _fetchData();
      });
    } else if (!hasProcessing) {
      _statusTimer?.cancel();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Moje Przepisy')),
      body: _buildBody(),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const UploadRecipeScreen()),
          );

          if (result == true) {
            setState(() {
              _isLoading = true;
            });
            _fetchData();
          }
        },
        child: const Icon(Icons.add_a_photo),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _recipes.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    } else if (_error != null && _recipes.isEmpty) {
      return Center(child: Text(_error!));
    } else if (_recipes.isEmpty) {
      return RefreshIndicator(
        onRefresh: _fetchData,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          children: [
            SizedBox(
              height: MediaQuery.of(context).size.height * 0.5,
              child: const Center(
                child: Text("Brak przepisów. Dodaj nowy skan!"),
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _fetchData,
      child: ListView.separated(
        padding: const EdgeInsets.all(8),
        itemCount: _recipes.length,
        separatorBuilder: (context, index) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final recipe = _recipes[index];
                final bool isReady = recipe.status == 'processed';

                return ListTile(
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  leading: isReady
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: Image.network(
                            '${ApiService.baseUrl}${recipe.thumbnailUrl}',
                            width: 55,
                            height: 55,
                            fit: BoxFit.cover,
                            errorBuilder: (c, e, s) =>
                                const Icon(Icons.broken_image, size: 55),
                          ),
                        )
                      : const SizedBox(
                          width: 55,
                          height: 55,
                          child: Center(
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.orange,
                            ),
                          ),
                        ),
                  title: Text(
                    recipe.title,
                    style: TextStyle(
                      fontWeight: isReady ? FontWeight.bold : FontWeight.normal,
                      color: isReady ? Colors.black : Colors.grey[600],
                    ),
                  ),
                  subtitle: Padding(
                    padding: const EdgeInsets.only(top: 4.0),
                    child: Text(
                      isReady ? recipe.shortText : "Trwa analiza dokumentu...",
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 13,
                        fontStyle: isReady
                            ? FontStyle.normal
                            : FontStyle.italic,
                      ),
                    ),
                  ),
                  trailing: isReady
                      ? const Icon(Icons.arrow_forward_ios, size: 16)
                      : const Icon(
                          Icons.hourglass_bottom,
                          color: Colors.orange,
                        ),
                  onTap: isReady
                      ? () async {
                          await Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) =>
                                  RecipeDetailsScreen(recipeId: recipe.id),
                            ),
                          );
                          _fetchData();
                        }
                      : () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text(
                                'Proszę czekać, trwa rozpoznawanie tekstu...',
                              ),
                              duration: Duration(seconds: 1),
                            ),
                          );
                        },
                );
              },
            ),
    );
  }
}
