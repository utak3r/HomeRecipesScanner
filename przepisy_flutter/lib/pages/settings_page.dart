import 'package:flutter/material.dart';
import '../services/settings_service.dart';
import '../services/auth_service.dart';
import 'tags_management_page.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  final _settings = SettingsService();
  final _hostController = TextEditingController();
  final _portController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _hostController.text = _settings.host;
    _portController.text = _settings.port;
  }

  @override
  void dispose() {
    _hostController.dispose();
    _portController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    await _settings.setHost(_hostController.text.trim());
    await _settings.setPort(_portController.text.trim());

    if (!mounted) return;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Ustawienia zapisane')));
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ustawienia'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextField(
                controller: _hostController,
                decoration: const InputDecoration(
                  labelText: 'Host serwera',
                  hintText: 'np. 192.168.1.10',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.url,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _portController,
                decoration: const InputDecoration(
                  labelText: 'Port serwera',
                  hintText: 'np. 8000',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 32),
              if (AuthService().isAuthenticated) ...[
                ListTile(
                  leading: const Icon(Icons.tag, color: Colors.orange),
                  title: const Text('Zarządzaj tagami'),
                  subtitle: const Text('Edytuj lub usuwaj globalne tagi'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const TagsManagementPage(),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 48),
              ],

              ElevatedButton(
                onPressed: _save,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text('ZAPISZ'),
              ),
              if (AuthService().isAuthenticated) ...[
                const SizedBox(height: 16),
                OutlinedButton.icon(
                  onPressed: () async {
                    await AuthService().signOut();
                    if (mounted) {
                      Navigator.of(
                        context,
                      ).pushNamedAndRemoveUntil('/login', (route) => false);
                    }
                  },
                  icon: const Icon(Icons.logout),
                  label: const Text('WYLOGUJ SIĘ'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.red,
                    side: const BorderSide(color: Colors.red),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
