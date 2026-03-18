import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/tag.dart';

class TagsManagementPage extends StatefulWidget {
  const TagsManagementPage({super.key});

  @override
  State<TagsManagementPage> createState() => _TagsManagementPageState();
}

class _TagsManagementPageState extends State<TagsManagementPage> {
  final ApiService _apiService = ApiService();
  List<Tag> _tags = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchTags();
  }

  Future<void> _fetchTags() async {
    try {
      final tags = await _apiService.fetchTags();
      if (!mounted) return;
      setState(() {
        _tags = tags;
        _isLoading = false;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = 'Błąd: $e';
        _isLoading = false;
      });
    }
  }

  void _showEditTagDialog(Tag tag) {
    final controller = TextEditingController(text: tag.name);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edytuj tag'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(labelText: 'Nazwa taga'),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Anuluj'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (controller.text.isNotEmpty && controller.text != tag.name) {
                try {
                  await _apiService.updateTag(tag.id, controller.text);
                  if (context.mounted) {
                    Navigator.pop(context);
                    _fetchTags();
                  }
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context)
                        .showSnackBar(SnackBar(content: Text('Błąd: $e')));
                  }
                }
              } else {
                Navigator.pop(context);
              }
            },
            child: const Text('Zapisz'),
          ),
        ],
      ),
    );
  }

  void _confirmDeleteTag(Tag tag) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Usuń tag'),
        content: Text(
            'Czy na pewno chcesz usunąć tag #${tag.name}? Zostanie on usunięty ze wszystkich przepisów.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Anuluj'),
          ),
          ElevatedButton(
            onPressed: () async {
              try {
                await _apiService.deleteTag(tag.id);
                if (context.mounted) {
                  Navigator.pop(context);
                  _fetchTags();
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context)
                      .showSnackBar(SnackBar(content: Text('Błąd: $e')));
                }
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Usuń', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Zarządzanie tagami'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : _tags.isEmpty
                  ? const Center(child: Text('Brak tagów'))
                  : ListView.builder(
                      itemCount: _tags.length,
                      itemBuilder: (context, index) {
                        final tag = _tags[index];
                        return ListTile(
                          title: Text('#${tag.name}'),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(
                                icon: const Icon(Icons.edit),
                                onPressed: () => _showEditTagDialog(tag),
                              ),
                              IconButton(
                                icon: const Icon(Icons.delete),
                                color: Colors.red,
                                onPressed: () => _confirmDeleteTag(tag),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
    );
  }
}
