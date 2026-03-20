import 'package:google_sign_in/google_sign_in.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  GoogleSignIn? _googleSignIn;
  String? _idToken;
  static const String _tokenKey = 'auth_id_token';

  Future<void> init() async {
    final clientId = dotenv.env['GOOGLE_CLIENT_ID_ANDROID'];
    _googleSignIn = GoogleSignIn(
      clientId: clientId,
      scopes: ['email', 'openid', 'profile'],
    );

    final prefs = await SharedPreferences.getInstance();
    _idToken = prefs.getString(_tokenKey);

    if (_idToken != null) {
      await silentSignIn();
    }
  }

  bool get isAuthenticated => _idToken != null;
  String? get idToken => _idToken;

  Future<bool> signIn() async {
    try {
      final googleUser = await _googleSignIn?.signIn();
      if (googleUser == null) return false;

      final googleAuth = await googleUser.authentication;
      _idToken = googleAuth.idToken;

      if (_idToken != null) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_tokenKey, _idToken!);
        return true;
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
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  Future<bool> silentSignIn() async {
    try {
      final googleUser = await _googleSignIn?.signInSilently();
      if (googleUser != null) {
        final googleAuth = await googleUser.authentication;
        _idToken = googleAuth.idToken;
        if (_idToken != null) {
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString(_tokenKey, _idToken!);
          return true;
        }
      }
    } catch (e) {
      print('Błąd silent sign-in: $e');
    }
    return false;
  }
}
