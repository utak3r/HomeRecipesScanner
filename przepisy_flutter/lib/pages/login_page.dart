import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  bool _isLoggingIn = false;

  Future<void> _handleSignIn() async {
    setState(() {
      _isLoggingIn = true;
    });

    final success = await AuthService().signIn();

    if (mounted) {
      setState(() {
        _isLoggingIn = false;
      });

      if (success) {
        Navigator.of(context).pushReplacementNamed('/home');
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Błąd logowania przez Google')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Colors.orange[100]!, Colors.white],
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset('assets/icon/baza_przepisow_icon.png', height: 150),
            const SizedBox(height: 24),
            Text(
              'Baza Przepisów',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.orange[900],
              ),
            ),
            const SizedBox(height: 8),
            const Text('Zaloguj się, aby kontynuować'),
            const SizedBox(height: 48),
            if (_isLoggingIn)
              const CircularProgressIndicator()
            else
              ElevatedButton.icon(
                onPressed: _handleSignIn,
                icon: Image.asset('assets/images/google_logo.png'),
                label: const Text('Zaloguj się przez Google'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
                  backgroundColor: Colors.white,
                  foregroundColor: Colors.black87,
                ),
              ),
          ],
        ),
      ),
    );
  }
}
