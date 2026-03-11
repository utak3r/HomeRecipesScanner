import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/recipe.dart';

class ApiService {
  // Użyj adresu IP swojego komputera w sieci lokalnej!
  static const String baseUrl = 'http://192.168.68.108:8000';

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
}
