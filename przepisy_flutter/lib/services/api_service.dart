import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/recipe.dart';

class ApiService {
  static const String baseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://192.168.68.108:8000',
  );

  Future<List<Recipe>> fetchRecipes() async {
    final response = await http.get(Uri.parse('$baseUrl/recipes/'));

    if (response.statusCode == 200) {
      List jsonResponse = json.decode(response.body);
      return jsonResponse.map((data) => Recipe.fromJson(data)).toList();
    } else {
      throw Exception('Błąd ładowania przepisów');
    }
  }

  Future<Map<String, dynamic>> fetchFullRecipe(int id) async {
    final response = await http.get(Uri.parse('$baseUrl/recipes/$id')); //

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Błąd ładowania szczegółów przepisu');
    }
  }

  Future<void> updateRecipeTitle(int id, String newTitle) async {
    final response = await http.put(
      Uri.parse('$baseUrl/recipes/$id'),
      headers: {'Content-Type': 'application/json; charset=UTF-8'},
      body: json.encode({'title': newTitle}),
    );

    if (response.statusCode != 200) {
      throw Exception('Błąd aktualizacji tytułu');
    }
  }

  Future<void> updateRecipeContent(
      int id, Map<String, dynamic> structured) async {
    final response = await http.put(
      Uri.parse('$baseUrl/recipes/$id'),
      headers: {'Content-Type': 'application/json; charset=UTF-8'},
      body: json.encode({'structured': structured}),
    );

    if (response.statusCode != 200) {
      throw Exception('Błąd aktualizacji treści przepisu');
    }
  }

  Future<void> reprocessRecipe(int id) async {
    final response = await http.post(
      Uri.parse('$baseUrl/recipes/$id/reprocess'),
    );

    if (response.statusCode != 200 && response.statusCode != 202) {
      throw Exception('Błąd podczas ponownego przetwarzania przepisu');
    }
  }

  Future<void> deleteRecipe(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/recipes/$id'),
    );

    if (response.statusCode != 200 && response.statusCode != 204) {
      throw Exception('Błąd podczas usuwania przepisu');
    }
  }
}

