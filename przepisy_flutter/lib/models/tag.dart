class Tag {
  final int id;
  final String name;

  Tag({
    required this.id,
    required this.name,
  });

  factory Tag.fromJson(dynamic json) {
    if (json is String) {
      return Tag(id: -1, name: json);
    }
    return Tag(
      id: json['id'] ?? -1,
      name: json['name'] ?? '',
    );
  }


  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
    };
  }
}
