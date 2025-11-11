# Easy Media Input Guide

Multiple easy ways to add your media files!

## 🚀 Method 1: Folder Mode (Easiest!)

Just point to a folder with your media:

```cmd
python main.py --folder "C:\Photos\Vacation" --description "Summer vacation 2024"
```

The tool automatically finds **all** images and videos in that folder!

**Drag & Drop Version:**

1. Put all your media in one folder
2. Drag the folder onto `quick-reel.bat`
3. Enter description
4. Done!

## 🎯 Method 2: Interactive Mode

Guided step-by-step prompts:

```cmd
python main.py --interactive
```

You'll be asked:
1. How to add media (folder, manual, or current folder)
2. Description
3. Music (optional)
4. Duration (optional)
5. Style (optional)

## 📁 Method 3: Current Folder

If your media is in the project folder:

```cmd
python main.py --folder . --description "My reel"
```

Or just use interactive mode and select option 3!

## 💻 Method 4: Command Line (Original Way)

**Individual files:**
```cmd
python main.py --images "photo1.jpg,photo2.jpg" --videos "clip1.mp4" --description "My reel"
```

**Glob patterns:**
```cmd
python main.py --images "*.jpg" --videos "*.mp4" --description "My reel"
```

**Full paths:**
```cmd
python main.py --images "C:\Photos\*.jpg" --description "My reel"
```

## 🎬 Complete Examples

### Example 1: Vacation Reel (Folder Mode)
```cmd
python main.py --folder "D:\Vacation Photos" --description "Amazing week in Hawaii with surfing and sunsets" --music "beach-vibes.mp3"
```

### Example 2: Birthday Party (Interactive)
```cmd
python main.py --interactive
```
Then select:
- 1 (folder mode)
- Enter: `D:\Birthday Party`
- Description: "Sarah's surprise 30th birthday celebration"
- Music: `happy-birthday.mp3`

### Example 3: Product Showcase (Current Folder)
Put all product photos in project folder, then:
```cmd
python main.py --folder . --description "Introducing our new premium coffee maker" --style professional --duration 15
```

### Example 4: Quick Test (Drag & Drop)
1. Drag your media folder onto `quick-reel.bat`
2. Type: "Test reel"
3. Press Enter

## 📋 Quick Reference

| Method | Command | Best For |
|--------|---------|----------|
| **Folder** | `--folder "path"` | All files in one place |
| **Interactive** | `--interactive` | Beginners, guided help |
| **Current** | `--folder .` | Media in project folder |
| **Drag & Drop** | Use `quick-reel.bat` | Quickest way |
| **Manual** | `--images` `--videos` | Specific file selection |

## 🎨 Pro Tips

### Organize Your Media First
```
My Project/
├── photos/
│   ├── IMG_001.jpg
│   ├── IMG_002.jpg
│   └── IMG_003.jpg
├── videos/
│   ├── VID_001.mp4
│   └── VID_002.mp4
└── music/
    └── background.mp3
```

Then:
```cmd
# Process photos
python main.py --folder "My Project\photos" --description "Photo montage"

# Process videos
python main.py --folder "My Project\videos" --description "Video compilation"

# Process everything (put all in one folder)
python main.py --folder "My Project\all media" --description "Complete story"
```

### Use Subfolders
Put media in subfolders by theme:
```
Vacation/
├── beach/
├── restaurants/
└── hotels/
```

Create separate reels:
```cmd
python main.py --folder "Vacation\beach" --description "Beach days"
python main.py --folder "Vacation\restaurants" --description "Food tour"
```

### Name Files Smartly
The tool processes files in alphabetical order:
```
01_intro.jpg
02_main.jpg
03_outro.jpg
```

Or by date:
```
2024-01-01_photo.jpg
2024-01-02_photo.jpg
```

## ❓ FAQ

**Q: Can I mix folders and files?**
A: No, choose one method. But you can run the tool multiple times!

**Q: Does it search subfolders?**
A: No, only the specified folder. Move all media to one folder first.

**Q: What if I have both photos and videos?**
A: No problem! The tool automatically finds both.

**Q: Can I preview before rendering?**
A: Not yet, but you can do a quick test with `--duration 5` first.

**Q: Does the order matter?**
A: Files are processed alphabetically. The AI then selects the best moments.

## 🔄 Workflow Recommendation

**Best workflow:**

1. **Organize**: Put all media in one folder
2. **Choose method**:
   - Beginners → Interactive mode
   - Quick → Drag & Drop
   - Power users → Folder mode with options
3. **Test**: Create a short 10s reel first
4. **Refine**: Adjust description and create full reel

**Example:**
```cmd
# Test run (10 seconds)
python main.py --folder "Media" --description "Test" --duration 10

# Looks good? Create full reel
python main.py --folder "Media" --description "Amazing summer vacation with friends at the beach" --duration 30 --music "summer-vibes.mp3" --style engaging
```

---

**The easiest way:** Just drag your folder onto `quick-reel.bat` and you're done! 🎉
