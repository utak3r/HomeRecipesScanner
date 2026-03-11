class Recipe {
  final int id;
  final String title;
  final String thumbnailUrl;
  final String shortText;
  final String status;

  Recipe({
    required this.id,
    required this.title,
    required this.thumbnailUrl,
    required this.shortText,
    required this.status,
  });

  factory Recipe.fromJson(Map<String, dynamic> json) {
    return Recipe(
      id: json['id'],
      title: json['title'] ?? 'Bez tytułu',
      thumbnailUrl: json['thumbnail_url'] ?? '',
      shortText: json['short_text'] ?? '',
      status: json['status'] ?? 'new',
    );
  }
}
