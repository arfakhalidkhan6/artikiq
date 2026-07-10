import 'package:flutter/material.dart';
import '../app.dart';
import 'sign_in_screen.dart';
import 'sign_up_screen.dart';
import 'chat_screen.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _nameController = TextEditingController();

  bool _isSignUpMode = false;
  bool _isLoading = false;
  String? _selectedGender;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  void _clearFields() {
    _emailController.clear();
    _passwordController.clear();
    _nameController.clear();
  }

  // Visual helper function to display constraint validation errors on screen
  void _showAlert(String message, {Color backgroundColor = Colors.redAccent}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: backgroundColor,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  // Central constraint validation function
  bool _hasValidInputs() {
    final email = _emailController.text.trim();
    final password = _passwordController.text;

    // 1. Email Constraints
    if (email.isEmpty) {
      _showAlert('Email cannot be empty.');
      return false;
    }
    // Check for standard email structure layout
    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegex.hasMatch(email)) {
      _showAlert('Please enter a valid email format (e.g., name@email.com).');
      return false;
    }
    // CONSTRAINT: Email must contain at least one number
    if (!RegExp(r'\d').hasMatch(email)) {
      _showAlert('Email must contain at least one number.');
      return false;
    }

    // 2. Password Constraints
    if (password.isEmpty) {
      _showAlert('Password cannot be empty.');
      return false;
    }
    if (password.length < 6) {
      _showAlert('Password must be at least 6 characters long.');
      return false;
    }

    // CONSTRAINT: Password must be a mix of letters AND numbers
    final hasLetters = RegExp(r'[a-zA-Z]').hasMatch(password);
    final hasNumbers = RegExp(r'\d').hasMatch(password);
    if (!hasLetters || !hasNumbers) {
      _showAlert('Password must be a mix of both letters and numbers.');
      return false;
    }

    // 3. Full Name Constraint (Only enforced during Sign Up)
    if (_isSignUpMode && _nameController.text.trim().isEmpty) {
      _showAlert('Please enter your full name.');
      return false;
    }

    return true;
  }

  Future<void> _handleSignIn() async {
    if (!_hasValidInputs()) return;

    setState(() => _isLoading = true);
    try {
      await supabase.auth.signInWithPassword(
        email: _emailController.text.trim(),
        password: _passwordController.text,
      );
    } catch (e) {
      _showAlert('Sign In Failed: Invalid email or incorrect password.');
    }
    setState(() => _isLoading = false);
  }

  Future<void> _handleSignUp() async {
    if (!_hasValidInputs()) return;

    setState(() => _isLoading = true);
    try {
      // 1. Create user account on Supabase
      final res = await supabase.auth.signUp(
        email: _emailController.text.trim(),
        password: _passwordController.text,
      );

      if (res.user?.id != null) {
        // 2. Insert custom profile data
        await supabase.from('profiles').insert({
          'id': res.user!.id,
          'full_name': _nameController.text.trim(),
          'gender': _selectedGender,
          'updated_at': DateTime.now().toIso8601String(),
        });

        // NAVIGATION LOGIC: Force state change back to sign-in screen
        // and sign out immediately in case Supabase auto-logged them in.
        await supabase.auth.signOut();

        _clearFields();
        setState(() {
          _isSignUpMode = false; // Toggles the view to SignInScreen
        });

        _showAlert(
          'Account created successfully! Please sign in.',
          backgroundColor: Colors.green,
        );
      }
    } catch (e) {
      _showAlert('Sign Up Failed: Email might already be registered.');
    }
    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder(
      stream: supabase.auth.onAuthStateChange,
      builder: (context, snapshot) {
        final session = snapshot.data?.session;

        if (session != null) {
          return const ChatScreen();
        }

        return Scaffold(
          backgroundColor: const Color(0xFFF8FAFB),
          body: Center(
            child: SingleChildScrollView(
              child: _isSignUpMode
                  ? SignUpScreen(
                      key: UniqueKey(),
                      nameController: _nameController,
                      emailController: _emailController,
                      passwordController: _passwordController,
                      selectedGender: _selectedGender,
                      isLoading: _isLoading,
                      onGenderChanged: (val) =>
                          setState(() => _selectedGender = val),
                      onSignUpPressed: _handleSignUp,
                      onToggleMode: () {
                        _clearFields();
                        setState(() => _isSignUpMode = false);
                      },
                    )
                  : SignInScreen(
                      key: UniqueKey(),
                      emailController: _emailController,
                      passwordController: _passwordController,
                      isLoading: _isLoading,
                      onSignInPressed: _handleSignIn,
                      onToggleMode: () {
                        _clearFields();
                        setState(() => _isSignUpMode = true);
                      },
                    ),
            ),
          ),
        );
      },
    );
  }
}
