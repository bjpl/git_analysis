# Mobile & Desktop Applications File Types Guide

## Overview
Cross-platform development enables building applications that run on multiple operating systems from a single codebase. This guide covers file types for mobile and desktop application development.

## File Types Reference

| **Platform** | **Core Files** | **Supporting Files** | **Purpose** |
|-------------|----------------|---------------------|------------|
| **Electron Apps** | `.js`, `.html`, `.css` | `package.json`, `electron.js` | Cross-platform desktop apps |
| **React Native** | `.js`, `.jsx`, `.tsx` | `.gradle`, `.pbxproj`, `.json` | Cross-platform mobile apps |
| **Flutter Apps** | `.dart` | `pubspec.yaml`, `.json` | Multi-platform applications |

## Use Cases & Examples

### Electron Desktop Applications
**Best For:** Desktop tools, code editors, database clients
```javascript
// main.js - Electron main process
const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'assets/icon.png')
  });

  // Load the app
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile('dist/index.html');
  }

  // Create application menu
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow.webContents.send('menu-new');
          }
        },
        {
          label: 'Open',
          accelerator: 'CmdOrCtrl+O',
          click: () => {
            mainWindow.webContents.send('menu-open');
          }
        },
        { type: 'separator' },
        {
          label: 'Quit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => app.quit()
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// IPC communication
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('show-save-dialog', async () => {
  const { dialog } = require('electron');
  const result = await dialog.showSaveDialog(mainWindow, {
    filters: [
      { name: 'JSON Files', extensions: ['json'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result;
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
```

**Preload Script:**
```javascript
// preload.js - Bridge between main and renderer
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getVersion: () => ipcRenderer.invoke('get-app-version'),
  showSaveDialog: () => ipcRenderer.invoke('show-save-dialog'),
  onMenuAction: (callback) => {
    ipcRenderer.on('menu-new', callback);
    ipcRenderer.on('menu-open', callback);
  }
});
```
**Example Projects:** VS Code, Discord, Slack desktop apps

### React Native Mobile Applications
**Best For:** iOS/Android apps, social media apps, e-commerce
```javascript
// App.js - React Native main component
import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  Text,
  View,
  FlatList,
  TouchableOpacity,
  TextInput,
  Platform
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

const Stack = createStackNavigator();

// Home Screen Component
function HomeScreen({ navigation }) {
  const [todos, setTodos] = useState([]);
  const [inputText, setInputText] = useState('');

  useEffect(() => {
    loadTodos();
  }, []);

  const loadTodos = async () => {
    try {
      const stored = await AsyncStorage.getItem('todos');
      if (stored) setTodos(JSON.parse(stored));
    } catch (error) {
      console.error('Error loading todos:', error);
    }
  };

  const saveTodos = async (newTodos) => {
    try {
      await AsyncStorage.setItem('todos', JSON.stringify(newTodos));
    } catch (error) {
      console.error('Error saving todos:', error);
    }
  };

  const addTodo = () => {
    if (inputText.trim()) {
      const newTodo = {
        id: Date.now().toString(),
        text: inputText,
        completed: false
      };
      const newTodos = [...todos, newTodo];
      setTodos(newTodos);
      saveTodos(newTodos);
      setInputText('');
    }
  };

  const toggleTodo = (id) => {
    const newTodos = todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    );
    setTodos(newTodos);
    saveTodos(newTodos);
  };

  const renderTodo = ({ item }) => (
    <TouchableOpacity
      style={styles.todoItem}
      onPress={() => toggleTodo(item.id)}
    >
      <Text style={[
        styles.todoText,
        item.completed && styles.completedText
      ]}>
        {item.text}
      </Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>My Todos</Text>
      </View>
      
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Add a new todo..."
          onSubmitEditing={addTodo}
        />
        <TouchableOpacity style={styles.addButton} onPress={addTodo}>
          <Text style={styles.addButtonText}>Add</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={todos}
        renderItem={renderTodo}
        keyExtractor={item => item.id}
        style={styles.list}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#4a90e2',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 10,
    marginRight: 10,
    backgroundColor: 'white',
  },
  addButton: {
    backgroundColor: '#4a90e2',
    padding: 10,
    borderRadius: 5,
    justifyContent: 'center',
  },
  addButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  list: {
    flex: 1,
  },
  todoItem: {
    backgroundColor: 'white',
    padding: 15,
    marginHorizontal: 10,
    marginVertical: 5,
    borderRadius: 5,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 3,
      },
      android: {
        elevation: 3,
      },
    }),
  },
  todoText: {
    fontSize: 16,
  },
  completedText: {
    textDecorationLine: 'line-through',
    color: '#999',
  },
});

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```
**Example Projects:** Instagram clone, fitness tracker, food delivery app

### Flutter Cross-Platform Apps
**Best For:** Multi-platform from single codebase, performance-critical apps
```dart
// main.dart - Flutter application
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Task Manager',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: TaskListScreen(),
    );
  }
}

class Task {
  String id;
  String title;
  bool completed;
  DateTime createdAt;

  Task({
    required this.id,
    required this.title,
    this.completed = false,
    required this.createdAt,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'completed': completed,
    'createdAt': createdAt.toIso8601String(),
  };

  factory Task.fromJson(Map<String, dynamic> json) => Task(
    id: json['id'],
    title: json['title'],
    completed: json['completed'],
    createdAt: DateTime.parse(json['createdAt']),
  );
}

class TaskListScreen extends StatefulWidget {
  @override
  _TaskListScreenState createState() => _TaskListScreenState();
}

class _TaskListScreenState extends State<TaskListScreen> {
  List<Task> tasks = [];
  final TextEditingController _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadTasks();
  }

  Future<void> _loadTasks() async {
    final prefs = await SharedPreferences.getInstance();
    final String? tasksJson = prefs.getString('tasks');
    if (tasksJson != null) {
      final List<dynamic> tasksList = json.decode(tasksJson);
      setState(() {
        tasks = tasksList.map((t) => Task.fromJson(t)).toList();
      });
    }
  }

  Future<void> _saveTasks() async {
    final prefs = await SharedPreferences.getInstance();
    final String tasksJson = json.encode(tasks.map((t) => t.toJson()).toList());
    await prefs.setString('tasks', tasksJson);
  }

  void _addTask() {
    if (_controller.text.isNotEmpty) {
      setState(() {
        tasks.add(Task(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          title: _controller.text,
          createdAt: DateTime.now(),
        ));
      });
      _controller.clear();
      _saveTasks();
    }
  }

  void _toggleTask(String id) {
    setState(() {
      final task = tasks.firstWhere((t) => t.id == id);
      task.completed = !task.completed;
    });
    _saveTasks();
  }

  void _deleteTask(String id) {
    setState(() {
      tasks.removeWhere((t) => t.id == id);
    });
    _saveTasks();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Task Manager'),
        actions: [
          IconButton(
            icon: Icon(Icons.delete_sweep),
            onPressed: () {
              setState(() {
                tasks.removeWhere((t) => t.completed);
              });
              _saveTasks();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: EdgeInsets.all(16.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: 'Add a new task...',
                      border: OutlineInputBorder(),
                    ),
                    onSubmitted: (_) => _addTask(),
                  ),
                ),
                SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _addTask,
                  child: Text('Add'),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: tasks.length,
              itemBuilder: (context, index) {
                final task = tasks[index];
                return ListTile(
                  leading: Checkbox(
                    value: task.completed,
                    onChanged: (_) => _toggleTask(task.id),
                  ),
                  title: Text(
                    task.title,
                    style: TextStyle(
                      decoration: task.completed
                          ? TextDecoration.lineThrough
                          : TextDecoration.none,
                    ),
                  ),
                  subtitle: Text(
                    'Created: ${task.createdAt.toString().split('.')[0]}',
                  ),
                  trailing: IconButton(
                    icon: Icon(Icons.delete),
                    onPressed: () => _deleteTask(task.id),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
```
**Example Projects:** Shopping apps, banking apps, social networks

## Best Practices

1. **Platform Guidelines:** Follow iOS/Android/Desktop design guidelines
2. **Performance:** Optimize for mobile constraints (battery, memory)
3. **Offline Support:** Implement offline functionality
4. **Testing:** Test on real devices and multiple OS versions
5. **Security:** Implement secure storage and communication
6. **Updates:** Plan for app updates and versioning

## File Organization Pattern
```
mobile-app/
├── src/
│   ├── components/
│   ├── screens/
│   ├── navigation/
│   └── services/
├── ios/
│   └── [iOS specific files]
├── android/
│   └── [Android specific files]
├── assets/
│   ├── images/
│   └── fonts/
└── __tests__/
```

## Platform-Specific Considerations

### iOS Configuration
```xml
<!-- Info.plist -->
<key>NSCameraUsageDescription</key>
<string>This app needs camera access to take photos</string>
<key>NSLocationWhenInUseUsageDescription</key>
<string>This app needs location access to show nearby places</string>
```

### Android Configuration
```xml
<!-- AndroidManifest.xml -->
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-feature android:name="android.hardware.camera" android:required="false" />
```

## Performance Optimization
- Code splitting and lazy loading
- Image optimization for different screen densities
- Native module integration for performance-critical code
- Memory management and profiling
- Background task optimization

## Development Tools
- **Electron:** Electron Forge, Electron Builder
- **React Native:** Expo, React Native CLI, Flipper
- **Flutter:** Flutter DevTools, Android Studio, Xcode
- **Testing:** Detox, Appium, Flutter Driver
- **Distribution:** App Store Connect, Google Play Console