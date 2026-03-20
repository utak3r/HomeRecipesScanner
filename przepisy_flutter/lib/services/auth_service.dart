import 'dart:async';
import 'dart:convert';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'settings_service.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  GoogleSignIn? _googleSignIn;
  String? _idToken;
  String? _backendToken;
  
  static const String _tokenKey = 'auth_id_token';
  static const String _backendTokenKey = 'auth_backend_token';

  Future<void> init() async {
    final clientId = dotenv.env['GOOGLE_CLIENT_ID_ANDROID'];
    _googleSignIn = GoogleSignIn(
      clientId: clientId,
      scopes: ['email', 'openid', 'profile'],
    );

    final prefs = await SharedPreferences.getInstance();
    _idToken = prefs.getString(_tokenKey);
    _backendToken = prefs.getString(_backendTokenKey);

    // If we have a backend token, we consider ourselves logged in.
    // We can still try silent sign in to refresh the Google token if needed.
    if (_backendToken != null) {
      silentSignIn(); // Refresh in background
    }
  }

  bool get isAuthenticated => _backendToken != null;
  String? get idToken => _idToken;
  String? get backendToken => _backendToken;

  Future<bool> signIn() async {
    try {
      print('Starting Google Sign-In...');
      final googleUser = await _googleSignIn?.signIn();
      if (googleUser == null) {
        print('Google Sign-In cancelled by user');
        return false;
      }

      print('Google Sign-In successful, getting authentication...');
      final googleAuth = await googleUser.authentication;
      _idToken = googleAuth.idToken;

      if (_idToken != null) {
        print('Exchanging Google ID Token for Backend JWT...');
        final success = await _exchangeForBackendToken(_idToken!);
        if (success) {
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString(_tokenKey, _idToken!);
          return true;
        }
      } else {
        print('Error: Google ID Token is null');
      }
      return false;
    } catch (e) {
      print('Błąd Google Sign-In: $e');
      return false;
    }
  }

  Future<void> signOut() async {
    await _googleSignIn?.signOut();
    _idToken = null;
    _backendToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_backendTokenKey);
  }

  Future<bool> silentSignIn() async {
    try {
      final googleUser = await _googleSignIn?.signInSilently();
      if (googleUser != null) {
        final googleAuth = await googleUser.authentication;
        _idToken = googleAuth.idToken;
        if (_idToken != null) {
          final success = await _exchangeForBackendToken(_idToken!);
          if (success) {
            final prefs = await SharedPreferences.getInstance();
            await prefs.setString(_tokenKey, _idToken!);
            return true;
          }
        }
      }
    } catch (e) {
      print('Błąd silent sign-in: $e');
    }
    return false;
  }

  Future<bool> _exchangeForBackendToken(String googleIdToken) async {
    try {
      final baseUrl = SettingsService().baseUrl;
      print('Attempting backend login at: $baseUrl/auth/login');
      
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'id_token': googleIdToken}),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _backendToken = data['access_token'];
        if (_backendToken != null) {
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString(_backendTokenKey, _backendToken!);
          print('Backend login successful');
          return true;
        }
      } else {
        print('Backend login failed: ${response.statusCode} ${response.body}');
      }
    } on TimeoutException catch (_) {
      print('Błąd: Przekroczono czas oczekiwania na odpowiedź serwera backendu.');
    } catch (e) {
      print('Błąd wymiany tokena na backendowy: $e');
    }
    return false;
  }
}
