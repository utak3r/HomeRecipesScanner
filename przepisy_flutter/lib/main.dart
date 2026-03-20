import 'package:flutter/material.dart';
import 'dart:async';
import 'services/api_service.dart';
import 'models/recipe.dart';
import 'models/tag.dart';
import 'pages/recipe_details_screen.dart';
import 'pages/upload_recipe_screen.dart';

import 'services/settings_service.dart';
import 'pages/settings_page.dart';
import 'services/auth_service.dart';
import 'pages/login_page.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");
  await SettingsService().init();
  await AuthService().init();
  runApp(const RecipeApp());
}

class RecipeApp extends StatelessWidget {
  const RecipeApp({super.key});

  @override
  Widget build(BuildContext context) {
    final bool isLoggedIn = AuthService().isAuthenticated;

    return MaterialApp(
      title: 'Baza Przepisów',
      theme: ThemeData(primarySwatch: Colors.orange, useMaterial3: true),
      home: isLoggedIn ? const RecipeListScreen() : const LoginPage(),
      routes: {
        '/login': (context) => const LoginPage(),
        '/home': (context) => const RecipeListScreen(),
        '/settings': (context) => const SettingsPage(),
      },
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
  final TextEditingController _searchController = TextEditingController();
  Timer? _statusTimer;
  List<Recipe> _recipes = [];
  List<Tag> _allTags = [];
  String? _selectedTagName;
  String _searchQuery = '';
  bool _isLoading = true;
  String? _error;
  Timer? _debounce;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  @override
  void dispose() {
    _statusTimer?.cancel();
    _debounce?.cancel();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _fetchData() async {
    try {
      final List<Recipe> data;
      if (_searchQuery.isNotEmpty) {
        data = await apiService.searchRecipes(_searchQuery);
      } else if (_selectedTagName != null) {
        data = await apiService.fetchRecipesByTag(_selectedTagName!);
      } else {
        data = await apiService.fetchRecipes();
      }
      final tags = await apiService.fetchTags();

      if (!mounted) return;
      setState(() {
        _recipes = data;
        _allTags = tags;
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
    bool hasActiveProcessing = _recipes.any(
      (r) => r.status == 'new' || r.status == 'processing',
    );

    if (hasActiveProcessing &&
        (_statusTimer == null || !_statusTimer!.isActive)) {
      _statusTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
        _fetchData();
      });
    } else if (!hasActiveProcessing) {
      _statusTimer?.cancel();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Moje Przepisy'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () async {
              await Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const SettingsPage()),
              );
              // Po powrocie z ustawień odświeżamy dane (w razie zmiany hosta)
              _fetchData();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          _buildSearchBar(),
          if (_allTags.isNotEmpty) _buildTagFilter(),
          Expanded(child: _buildBody()),
        ],
      ),
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

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.all(12.0),
      child: TextField(
        controller: _searchController,
        decoration: InputDecoration(
          hintText: 'Szukaj przepisów...',
          prefixIcon: const Icon(Icons.search),
          suffixIcon: _searchController.text.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () {
                    _searchController.clear();
                    setState(() {
                      _searchQuery = '';
                      _isLoading = true;
                    });
                    _fetchData();
                  },
                )
              : null,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          filled: true,
          fillColor: Colors.grey[100],
          contentPadding: const EdgeInsets.symmetric(vertical: 0),
        ),
        onChanged: (value) {
          if (_debounce?.isActive ?? false) _debounce!.cancel();
          _debounce = Timer(const Duration(milliseconds: 500), () {
            setState(() {
              _searchQuery = value;
              _isLoading = true;
            });
            _fetchData();
          });
        },
        onSubmitted: (value) {
          setState(() {
            _searchQuery = value;
            _isLoading = true;
          });
          _fetchData();
        },
      ),
    );
  }

  Widget _buildTagFilter() {
    return Container(
      height: 50,
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        itemCount: _allTags.length + 1,
        itemBuilder: (context, index) {
          if (index == 0) {
            return Padding(
              padding: const EdgeInsets.only(right: 8.0),
              child: FilterChip(
                label: const Text('Wszystkie'),
                selected: _selectedTagName == null,
                onSelected: (selected) {
                  if (selected) {
                    setState(() {
                      _selectedTagName = null;
                      _isLoading = true;
                    });
                    _fetchData();
                  }
                },
              ),
            );
          }
          final tag = _allTags[index - 1];
          return Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: FilterChip(
              label: Text(tag.name),
              selected: _selectedTagName == tag.name,
              onSelected: (selected) {
                setState(() {
                  _selectedTagName = selected ? tag.name : null;
                  _isLoading = true;
                });
                _fetchData();
              },
            ),
          );
        },
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
              child: Center(
                child: Text(
                  _selectedTagName != null
                      ? "Brak przepisów z tagiem #$_selectedTagName"
                      : "Brak przepisów. Dodaj nowy skan!",
                ),
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
          final bool isBusy =
              recipe.status == 'new' || recipe.status == 'processing';
          final bool isReady = recipe.status == 'processed';
          final bool isFailed = recipe.status == 'failed';

          return ListTile(
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 8,
            ),
            leading: isBusy
                ? const SizedBox(
                    width: 55,
                    height: 55,
                    child: Center(
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.orange,
                      ),
                    ),
                  )
                : ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: Image.network(
                      recipe.thumbnailUrl,
                      width: 55,
                      height: 55,
                      fit: BoxFit.cover,
                      errorBuilder: (c, e, s) =>
                          const Icon(Icons.broken_image, size: 55),
                    ),
                  ),
            title: Text(
              recipe.title,
              style: TextStyle(
                fontWeight: isReady ? FontWeight.bold : FontWeight.normal,
                color: isReady
                    ? Colors.black
                    : (isFailed ? Colors.red[700] : Colors.grey[600]),
              ),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: 4.0),
                  child: Text(
                    isReady
                        ? recipe.shortText
                        : (isFailed
                              ? "Błąd przetwarzania - kliknij, aby sprawdzić"
                              : "Trwa analiza dokumentu..."),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 13,
                      fontStyle: isReady ? FontStyle.normal : FontStyle.italic,
                      color: isFailed ? Colors.red[400] : null,
                    ),
                  ),
                ),
                if (recipe.tags.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 6.0),
                    child: Wrap(
                      spacing: 4,
                      runSpacing: 4,
                      children: <Widget>[
                        ...recipe.tags
                            .take(3)
                            .map(
                              (tag) => Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 6,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.orange[100],
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: Text(
                                  '#${tag.name}',
                                  style: TextStyle(
                                    fontSize: 10,
                                    color: Colors.orange[900],
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ),
                            ),
                        if (recipe.tags.length > 3)
                          const Text(
                            '...',
                            style: TextStyle(fontSize: 10, color: Colors.grey),
                          ),
                      ],
                    ),
                  ),
              ],
            ),
            trailing: isBusy
                ? const Icon(Icons.hourglass_bottom, color: Colors.orange)
                : (isFailed
                      ? const Icon(Icons.error_outline, color: Colors.red)
                      : const Icon(Icons.arrow_forward_ios, size: 16)),
            onTap: isBusy
                ? () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text(
                          'Proszę czekać, trwa rozpoznawanie tekstu...',
                        ),
                        duration: Duration(seconds: 1),
                      ),
                    );
                  }
                : () async {
                    await Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            RecipeDetailsScreen(recipeId: recipe.id),
                      ),
                    );
                    _fetchData();
                  },
          );
        },
      ),
    );
  }
}
