import 'package:shared_preferences/shared_preferences.dart';

class SettingsService {
  static final SettingsService _instance = SettingsService._internal();
  factory SettingsService() => _instance;
  SettingsService._internal();

  late SharedPreferences _prefs;
  bool _isInitialized = false;

  static const String _keyHost = 'api_host';
  static const String _keyPort = 'api_port';

  // Default values matching original ApiService
  static const String _defaultHost = '192.168.68.113';
  static const String _defaultPort = '8000';

  Future<void> init() async {
    if (_isInitialized) return;
    _prefs = await SharedPreferences.getInstance();
    _isInitialized = true;
  }

  String get host => _prefs.getString(_keyHost) ?? _defaultHost;
  String get port => _prefs.getString(_keyPort) ?? _defaultPort;

  Future<void> setHost(String value) async {
    await _prefs.setString(_keyHost, value);
  }

  Future<void> setPort(String value) async {
    await _prefs.setString(_keyPort, value);
  }

  String get baseUrl {
    final h = host;
    final p = port;
    if (p.isEmpty) return 'http://$h';
    return 'http://$h:$p';
  }
}
