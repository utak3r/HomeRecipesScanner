import 'package:flutter/material.dart';
import '../services/api_service.dart';

class UrlUploadPage extends StatefulWidget {
  final String? initialUrl;
  const UrlUploadPage({super.key, this.initialUrl});

  @override
  State<UrlUploadPage> createState() => _UrlUploadPageState();
}

class _UrlUploadPageState extends State<UrlUploadPage> {
  late final TextEditingController _urlController;
  final ApiService _apiService = ApiService();
  bool _isSending = false;
  bool _isValid = false;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(text: widget.initialUrl);
    _urlController.addListener(_validate);
    _validate();
  }

  @override
  void dispose() {
    _urlController.removeListener(_validate);
    _urlController.dispose();
    super.dispose();
  }

  void _validate() {
    final text = _urlController.text.trim();
    setState(() {
      _isValid = text.isNotEmpty && (text.startsWith('http://') || text.startsWith('https://'));
    });
  }

  Future<void> _sendUrl() async {
    if (!_isValid) return;

    setState(() => _isSending = true);

    try {
      await _apiService.uploadRecipeFromUrl(_urlController.text.trim());
      if (!mounted) return;
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('URL wysłany do przetworzenia!')),
      );
      Navigator.pop(context, true);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Błąd: $e')),
      );
    } finally {
      if (mounted) {
        setState(() => _isSending = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dodaj z URL'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
        actions: [
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: 8.0,
              vertical: 8.0,
            ),
            child: IconButton.filled(
              onPressed: _isValid && !_isSending ? _sendUrl : null,
              icon: _isSending
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.send),
              style: IconButton.styleFrom(
                backgroundColor: Colors.green,
                foregroundColor: Colors.white,
                disabledBackgroundColor: Colors.grey,
              ),
            ),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Wklej link do strony z przepisem:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                hintText: 'https://example.com/przepis',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.link),
              ),
              keyboardType: TextInputType.url,
              autofocus: true,
              enabled: !_isSending,
              onSubmitted: (_) => _sendUrl(),
            ),
          ],
        ),
      ),
    );
  }
}
