import 'tag.dart';

class Recipe {
  final int id;
  final String title;
  final String thumbnailUrl;
  final String shortText;
  final String status;
  final List<Tag> tags;

  Recipe({
    required this.id,
    required this.title,
    required this.thumbnailUrl,
    required this.shortText,
    required this.status,
    this.tags = const [],
  });

  factory Recipe.fromJson(Map<String, dynamic> json) {
    var tagsFromJson = json['tags'] as List? ?? [];
    List<Tag> tagsList = tagsFromJson.map((t) => Tag.fromJson(t)).toList();

    return Recipe(
      id: json['id'],
      title: json['title'] ?? 'Bez tytułu',
      thumbnailUrl: json['thumbnail_url'] ?? '',
      shortText: json['short_text'] ?? '',
      status: json['status'] ?? 'new',
      tags: tagsList,
    );
  }
}

