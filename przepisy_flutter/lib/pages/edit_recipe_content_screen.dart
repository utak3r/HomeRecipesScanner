import 'package:flutter/material.dart';
import '../services/api_service.dart';

class _IngredientItem {
  String amount;
  String name;
  final Key key;
  _IngredientItem(this.amount, this.name) : key = UniqueKey();
}

class _StepItem {
  String text;
  final Key key;
  _StepItem(this.text) : key = UniqueKey();
}

class EditRecipeContentScreen extends StatefulWidget {
  final int recipeId;
  final Map<String, dynamic> initialStructured;

  const EditRecipeContentScreen({
    super.key,
    required this.recipeId,
    required this.initialStructured,
  });

  @override
  State<EditRecipeContentScreen> createState() =>
      _EditRecipeContentScreenState();
}

class _EditRecipeContentScreenState extends State<EditRecipeContentScreen> {
  late List<_IngredientItem> _ingredients;
  late List<_StepItem> _steps;
  late TextEditingController _notesController;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _ingredients = (widget.initialStructured['ingredients'] as List? ?? []).map(
      (e) {
        final map = e as Map;
        return _IngredientItem(
            map['amount']?.toString() ?? '', map['name']?.toString() ?? '');
      },
    ).toList();
    _steps = (widget.initialStructured['steps'] as List? ?? []).map(
      (e) => _StepItem(e.toString()),
    ).toList();
    _notesController = TextEditingController(
      text: widget.initialStructured['notes']?.toString() ?? '',
    );
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _saveChanges() async {
    setState(() => _isSaving = true);
    
    final finalIngredients = _ingredients.where((ing) {
      return ing.name.trim().isNotEmpty;
    }).map((ing) => {
      'amount': ing.amount.trim(),
      'name': ing.name.trim(),
    }).toList();
    
    final finalSteps = _steps.map((s) => s.text.trim()).where((s) => s.isNotEmpty).toList();

    final Map<String, dynamic> updatedStructured = {
      'ingredients': finalIngredients,
      'steps': finalSteps,
      if (_notesController.text.trim().isNotEmpty)
        'notes': _notesController.text.trim(),
    };

    try {
      await ApiService().updateRecipeContent(widget.recipeId, updatedStructured);
      if (mounted) {
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Błąd zapisu: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  void _addIngredient() {
    setState(() {
      _ingredients.add(_IngredientItem('', ''));
    });
  }

  void _removeIngredient(int index) {
    setState(() {
      _ingredients.removeAt(index);
    });
  }

  void _moveIngredientUp(int index) {
    if (index > 0) {
      setState(() {
        final item = _ingredients.removeAt(index);
        _ingredients.insert(index - 1, item);
      });
    }
  }

  void _moveIngredientDown(int index) {
    if (index < _ingredients.length - 1) {
      setState(() {
        final item = _ingredients.removeAt(index);
        _ingredients.insert(index + 1, item);
      });
    }
  }

  void _addStep() {
    setState(() {
      _steps.add(_StepItem(''));
    });
  }

  void _removeStep(int index) {
    setState(() {
      _steps.removeAt(index);
    });
  }

  void _moveStepUp(int index) {
    if (index > 0) {
      setState(() {
        final item = _steps.removeAt(index);
        _steps.insert(index - 1, item);
      });
    }
  }

  void _moveStepDown(int index) {
    if (index < _steps.length - 1) {
      setState(() {
        final item = _steps.removeAt(index);
        _steps.insert(index + 1, item);
      });
    }
  }

  Widget _buildIngredientItem(int index) {
    final ing = _ingredients[index];
    return Card(
      key: ing.key,
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Row(
          children: [
            Column(
              children: [
                IconButton(
                  icon: const Icon(Icons.arrow_upward),
                  onPressed: index > 0 ? () => _moveIngredientUp(index) : null,
                  constraints: const BoxConstraints(),
                  padding: EdgeInsets.zero,
                ),
                IconButton(
                  icon: const Icon(Icons.arrow_downward),
                  onPressed: index < _ingredients.length - 1
                      ? () => _moveIngredientDown(index)
                      : null,
                  constraints: const BoxConstraints(),
                  padding: EdgeInsets.zero,
                ),
              ],
            ),
            const SizedBox(width: 8),
            Expanded(
              flex: 1,
              child: TextFormField(
                initialValue: ing.amount,
                decoration: const InputDecoration(labelText: 'Ilość'),
                onChanged: (val) => ing.amount = val,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              flex: 2,
              child: TextFormField(
                initialValue: ing.name,
                decoration: const InputDecoration(labelText: 'Składnik'),
                onChanged: (val) => ing.name = val,
              ),
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: Colors.red),
              onPressed: () => _removeIngredient(index),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStepItem(int index) {
    final step = _steps[index];
    return Card(
      key: step.key,
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Column(
              children: [
                IconButton(
                  icon: const Icon(Icons.arrow_upward),
                  onPressed: index > 0 ? () => _moveStepUp(index) : null,
                  constraints: const BoxConstraints(),
                  padding: EdgeInsets.zero,
                ),
                IconButton(
                  icon: const Icon(Icons.arrow_downward),
                  onPressed:
                      index < _steps.length - 1 ? () => _moveStepDown(index) : null,
                  constraints: const BoxConstraints(),
                  padding: EdgeInsets.zero,
                ),
              ],
            ),
            const SizedBox(width: 8),
            Text('${index + 1}. ',
                style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(width: 8),
            Expanded(
              child: TextFormField(
                initialValue: step.text,
                decoration: const InputDecoration(
                  labelText: 'Krok przepisów',
                  border: OutlineInputBorder(),
                ),
                maxLines: null,
                onChanged: (val) => step.text = val,
              ),
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: Colors.red),
              onPressed: () => _removeStep(index),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edytuj treść przepisu'),
        actions: [
          if (_isSaving)
            const Center(
              child: Padding(
                padding: EdgeInsets.symmetric(horizontal: 16.0),
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Colors.white,
                  ),
                ),
              ),
            )
          else
            IconButton(
              icon: const Icon(Icons.save),
              onPressed: _saveChanges,
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Składniki',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                TextButton.icon(
                  onPressed: _addIngredient,
                  icon: const Icon(Icons.add),
                  label: const Text('Dodaj składnik'),
                )
              ],
            ),
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _ingredients.length,
              itemBuilder: (context, index) => _buildIngredientItem(index),
            ),
            const Divider(height: 32),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Kroki',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                TextButton.icon(
                  onPressed: _addStep,
                  icon: const Icon(Icons.add),
                  label: const Text('Dodaj krok'),
                )
              ],
            ),
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _steps.length,
              itemBuilder: (context, index) => _buildStepItem(index),
            ),
            const Divider(height: 32),
            const Text('Notatki (opcjonalnie)',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextFormField(
              controller: _notesController,
              decoration: const InputDecoration(
                hintText: 'Dodatkowe informacje...',
                border: OutlineInputBorder(),
              ),
              maxLines: 4,
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }
}
