# Enhanced Unsplash Image Search & GPT Description Tool

## 🚀 Production Build v2.0

This is the production-ready distribution of the Enhanced Unsplash Image Search application with advanced AI-powered Spanish language learning features.

## ✨ New Features

### 1. **Description Style Selector**
- **3 Distinct Styles**: Academic/Neutral, Poetic/Literary, Technical/Scientific
- **4 Vocabulary Levels**: Beginner, Intermediate, Advanced, Native
- **12 Total Configurations**: Each combination provides unique AI prompts

### 2. **Session-Based Image Variety**
- **Smart Rotation**: Different images for same search across sessions
- **Progressive Strategies**: 
  - Exploring (0-10 images)
  - Expanding (10-30 images)
  - Deep Search (30+ images)
- **Time-Based Seeds**: Hourly rotation for consistent variety
- **Fresh Search Button**: Reset history for completely new results

### 3. **Enhanced UI/UX**
- **Live Style Preview**: See example phrases for each style
- **Session Statistics**: Track search history and usage patterns
- **Persistent Preferences**: Saves your style and level choices
- **Visual Feedback**: Shows current page, strategy, and images shown

## 📋 Requirements

```bash
pip install -r requirements.txt
```

### Core Dependencies:
- `tkinter` (usually included with Python)
- `Pillow>=10.0.0`
- `requests>=2.31.0`
- `openai>=1.0.0` (optional, for AI descriptions)

## 🔧 Installation

1. **Clone or download** this distribution folder
2. **Install dependencies**:
   ```bash
   pip install Pillow requests openai
   ```
3. **Run the application**:
   ```bash
   python enhanced_image_search.py
   ```

## 🔑 API Configuration

The application requires two API keys:

1. **Unsplash Access Key**: For image search
   - Get it free at: https://unsplash.com/developers
   
2. **OpenAI API Key**: For AI descriptions (optional)
   - Get it at: https://platform.openai.com/api-keys

Configure keys via the menu: `File → Configure API Keys`

## 🎯 How to Use

### Basic Workflow:
1. **Enter a search term** (e.g., "sunset", "coffee", "mountain")
2. **Click Search** to find images with automatic variety
3. **Select your style** (Academic, Poetic, or Technical)
4. **Choose vocabulary level** (Beginner to Native)
5. **Generate Description** to get AI-powered Spanish text
6. **Use Shuffle** for different images from same search
7. **Click Fresh** to reset history and get completely new results

### Style Examples:

#### Academic Style (Intermediate):
> "Cabe destacar que la composición presenta elementos contrastantes que sugieren una narrativa visual coherente."

#### Poetic Style (Intermediate):
> "El lienzo respira historias susurradas por el viento, tejiendo memorias en cada trazo de luz."

#### Technical Style (Intermediate):
> "Las propiedades ópticas indican una reflexión especular del 30% con temperatura de color aproximada de 5500K."

## 📊 Session Management

### Image Variety Algorithm:
- **Pages 1-5**: First 10 images
- **Pages 1-10**: Images 10-30
- **Pages 1-100**: Advanced hash-based distribution for 30+ images
- **Hourly Seeds**: Ensures variety even for same page

### Data Storage:
- **Session History**: `data/search_sessions.json`
- **Image Records**: `data/image_history.json`
- **Configuration**: `data/config.json`
- **30-Day Retention**: Old data automatically cleaned

## 🎨 Customization

### Adding Custom Styles:
Edit the `DescriptionStyleManager._initialize_styles()` method to add your own style configurations.

### Modifying Vocabulary Levels:
Adjust the `StyleConfig` entries for each level to match your learning needs.

## 📈 Performance

- **Efficient Caching**: Session data cached in memory
- **Async Operations**: Non-blocking image loading
- **Smart Pagination**: Optimized API calls
- **Lightweight**: ~500KB total size
- **Cross-Platform**: Works on Windows, Mac, Linux

## 🐛 Troubleshooting

### Common Issues:

1. **"No module named 'PIL'"**
   ```bash
   pip install Pillow
   ```

2. **API Key Errors**
   - Verify keys in `File → Configure API Keys`
   - Check internet connection

3. **Images Not Loading**
   - Check Unsplash API quota (50 requests/hour free tier)
   - Verify search term returns results

## 📝 License

This enhanced version includes features inspired by best practices from various open-source projects. Use freely for educational purposes.

## 🆘 Support

For issues or feature requests, please refer to the main project repository.

---

**Version**: 2.0.0  
**Build Date**: 2025  
**Enhanced Features**: Style Selector, Session Variety, Smart Rotation